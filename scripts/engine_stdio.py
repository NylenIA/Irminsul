#!/usr/bin/env python3
"""Pont stdio one-shot vers le VRAI moteur Python (damage/reaction).

Protocole : une requête JSON sur stdin -> une réponse JSON sur stdout, puis exit.
  {"method": "calculate_direct_hit" | "amplifying_multiplier" | "transformative_reaction",
   "params": {...}}
Réponse : {"ok": true, "result": {...}, "engine": "python-sidecar"} | {"ok": false, "error": "..."}
Aucun secret, aucune écriture disque, borné (utilisé par SidecarEngineClient avec timeout).
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from irminsul.damage import calculate_direct_hit  # noqa: E402
from irminsul.reaction import amplifying_multiplier, transformative_reaction  # noqa: E402

METHODS = {
    "calculate_direct_hit": lambda p: calculate_direct_hit(**p).to_dict(),
    "amplifying_multiplier": lambda p: amplifying_multiplier(**p).to_dict(),
    "transformative_reaction": lambda p: transformative_reaction(**p).to_dict(),
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
