"""Sidecar moteur Irminsul : protocole stdin/stdout JSON **borné**, un coup par
processus (robuste : un appel ne peut pas corrompre un autre).

Requête (stdin, UTF-8, ≤ MAX_INPUT octets) : {"id": <any>, "method": str, "params": {}}
Réponse (stdout, UTF-8, objet unique) :
  succès → {"id", "ok": true, "result": {...}}
  erreur → {"id", "ok": false, "error": {"type": str, "message": str}}

Aucun secret n'est attendu ni journalisé ; la sortie standard ne contient QUE la
réponse JSON (les diagnostics éventuels vont sur stderr). Le moteur n'utilise que
la bibliothèque standard → empaquetable en exécutable autonome (PyInstaller).
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .engine_dispatch import dispatch  # dispatcher CANONIQUE (même table que le pont web)

MAX_INPUT = 2_000_000  # octets : borne la REQUÊTE (le fichier GOOD est lu par chemin)
PROTOCOL_VERSION = 1


def _enc(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")


def handle(data: bytes) -> bytes:
    """Traite une requête (bytes) et renvoie la réponse (bytes). Jamais d'exception."""
    req_id: Any = None
    try:
        if len(data) > MAX_INPUT:
            raise ValueError("requête trop volumineuse")
        if not data.strip():
            raise ValueError("requête vide")
        req = json.loads(data.decode("utf-8"))
        if not isinstance(req, dict):
            raise ValueError("requête : objet JSON attendu")
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}
        if not isinstance(method, str):
            raise ValueError("champ 'method' (str) requis")
        if not isinstance(params, dict):
            raise ValueError("champ 'params' : objet attendu")
        result = dispatch(method, params)
        return _enc({"id": req_id, "ok": True, "result": result})
    except json.JSONDecodeError as exc:
        return _enc({"id": req_id, "ok": False, "error": {"type": "invalid_json", "message": str(exc)}})
    except ValueError as exc:
        return _enc({"id": req_id, "ok": False, "error": {"type": "bad_request", "message": str(exc)}})
    except Exception as exc:  # noqa: BLE001 — toujours répondre proprement, sans masquer le type
        return _enc({"id": req_id, "ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}})


def main() -> int:
    data = sys.stdin.buffer.read(MAX_INPUT + 1)
    sys.stdout.buffer.write(handle(data))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
