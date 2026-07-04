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
