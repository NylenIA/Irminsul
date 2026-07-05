#!/usr/bin/env python3
"""Pont stdio one-shot vers le VRAI moteur Python (damage/reaction).

Protocole : une requête JSON sur stdin -> une réponse JSON sur stdout, puis exit.
  {"method": "calculate_direct_hit" | "amplifying_multiplier" | "transformative_reaction"
            | "character_final_stats",
   "params": {...}}
Réponse : {"ok": true, "result": {...}, "engine": "python-sidecar"} | {"ok": false, "error": "..."}
Aucun secret, aucune écriture disque, borné (utilisé par SidecarEngineClient avec timeout).
La provenance du compte est curée par le moteur (snapshot_date/source/sha256) — jamais de
chemin local ni de payload brut.
"""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from irminsul.damage import calculate_direct_hit  # noqa: E402
from irminsul.reaction import amplifying_multiplier, transformative_reaction  # noqa: E402

# Version du contrat API du sidecar (incrémentée si le protocole change).
SIDECAR_API_VERSION = "engine-stdio/1.0"


def _engine_provenance(_params: dict[str, Any]) -> dict[str, Any]:
    """Provenance du moteur, lisible par l'app (section diagnostic) — jamais de chemin local.

    Permet à l'UI de vérifier la PARITÉ : quel moteur/contrats répond réellement, plutôt que de
    supposer qu'un binaire au nom plausible correspond au code testé.
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    git_commit = None
    try:  # commit source si le .git est présent (dev) — absent en binaire empaqueté, c'est OK.
        head = (root / ".git" / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            ref = head.split(" ", 1)[1].strip()
            git_commit = (root / ".git" / ref).read_text(encoding="utf-8").strip()[:12]
        else:
            git_commit = head[:12]
    except Exception:  # noqa: BLE001
        git_commit = None
    frozen = getattr(sys, "frozen", False)  # True si exécuté depuis un binaire PyInstaller
    return {
        "engine": "python-sidecar",
        "api_version": SIDECAR_API_VERSION,
        "methods": sorted(METHODS.keys()),
        "contracts": {
            "direct_hit": "direct-hit@irminsul-damage",
            "reactions": "reactions/1.0",
            "final_stats": "final-stats/1.0",
            "rotation": "rotation/1.0",
        },
        "git_commit": git_commit,
        "frozen_binary": bool(frozen),
        "python": sys.version.split()[0],
    }


def _character_final_stats(params: dict[str, Any]) -> dict[str, Any]:
    """Stats finales d'un personnage du scan (moteur charstats, défensif, zéro invention)."""
    key = params.get("key")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("paramètre 'key' (nom du personnage) requis")
    from irminsul import charstats  # import paresseux : n'alourdit pas les calculs directs

    return charstats.character_payload(key.strip())


def _calculate_rotation(params: dict[str, Any]) -> dict[str, Any]:
    """Rotation chiffrée (moteur rotation, coefficients+stats réels, jamais de faux DPS)."""
    from irminsul import rotation  # import paresseux

    team = params.get("team")
    actions = params.get("actions")
    enemy = params.get("enemy") or {}
    if not isinstance(team, list):
        raise ValueError("paramètre 'team' (liste de personnages) requis")
    if not isinstance(actions, list):
        raise ValueError("paramètre 'actions' (liste) requis")
    return rotation.calculate_rotation(team, actions, enemy)


METHODS = {
    "calculate_direct_hit": lambda p: calculate_direct_hit(**p).to_dict(),
    "amplifying_multiplier": lambda p: amplifying_multiplier(**p).to_dict(),
    "transformative_reaction": lambda p: transformative_reaction(**p).to_dict(),
    "character_final_stats": _character_final_stats,
    "calculate_rotation": _calculate_rotation,
    "engine_provenance": _engine_provenance,
}

MAX_INPUT = 64 * 1024


def main() -> int:
    raw = sys.stdin.read(MAX_INPUT + 1)
    try:
        if len(raw) > MAX_INPUT:
            raise ValueError("requête trop grande")
        request = json.loads(raw)
        method = METHODS.get(request.get("method"))
        if method is None:
            raise ValueError(f"méthode inconnue : {request.get('method')!r}")
        params = request.get("params") or {}
        if not isinstance(params, dict):
            raise ValueError("params doit être un objet")
        result = method(params)
        print(json.dumps({"ok": True, "result": result, "engine": "python-sidecar"}))
        return 0
    except Exception as error:  # noqa: BLE001 — frontière de processus : erreur typée côté client
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
