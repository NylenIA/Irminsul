#!/usr/bin/env python3
"""Pont stdio one-shot vers le moteur Python — DÉLÈGUE au dispatcher CANONIQUE
(`irminsul.engine_dispatch`) : même table de méthodes que le binaire PyInstaller
(`irminsul.sidecar`). Plus aucune liste de méthodes locale ici.

Protocole (conservé pour SidecarEngineClient web) :
  stdin  : {"method": str, "params": {...}}   (≤ 64 Ko)
  stdout : {"ok": true, "result": {...}, "engine": "python-sidecar"}
           | {"ok": false, "error": "..."}
La provenance du protocole ajoute `api_version` (version du PONT stdio) à la provenance
canonique du moteur (`ipc_contract`, méthodes triées, frozen, build info).
"""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from irminsul.engine_dispatch import dispatch, engine_provenance  # noqa: E402

SIDECAR_API_VERSION = "engine-stdio/1.0"
MAX_INPUT = 64 * 1024


def _engine_provenance(params: dict[str, Any]) -> dict[str, Any]:
    """Provenance canonique + version du pont stdio (compat contrat existant)."""
    return {**engine_provenance(params), "api_version": SIDECAR_API_VERSION}


def main() -> int:
    raw = sys.stdin.read(MAX_INPUT + 1)
    try:
        if len(raw) > MAX_INPUT:
            raise ValueError("requête trop grande")
        request = json.loads(raw)
        method = request.get("method")
        if not isinstance(method, str):
            raise ValueError("champ 'method' (str) requis")
        params = request.get("params") or {}
        if not isinstance(params, dict):
            raise ValueError("params doit être un objet")
        # Le pont enrichit la provenance de sa propre version de protocole.
        if method == "engine_provenance":
            result: dict[str, Any] = _engine_provenance(params)
        else:
            result = dispatch(method, params)
        print(json.dumps({"ok": True, "result": result, "engine": "python-sidecar"}, default=str))
        return 0
    except Exception as error:  # noqa: BLE001 — frontière de processus : erreur typée côté client
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
