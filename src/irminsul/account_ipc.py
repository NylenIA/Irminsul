"""Pont IPC « moteur compte » pour l'app desktop : sortie **JSON pure** (sans rich).

Le frontend (via une commande Tauri) appelle `python -m irminsul.account_ipc <cmd>`.
Contrat stable, machine-lisible, avec provenance et fraîcheur. Ne renvoie jamais de
donnée factice : si aucun compte n'est importé, renvoie `{"status": "empty"}`.

Commandes : `profile` · `overview` · `import-good <chemin>`.
"""

from __future__ import annotations

import json
import sys

from .account import build_overview, import_good, load_current


def _emit(obj: object) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, default=str))


def cmd_profile() -> None:
    try:
        cur = load_current()
    except FileNotFoundError:
        _emit({"status": "empty", "message": "Aucun compte importé."})
        return
    p = cur["account-profile"]
    _emit({
        "status": "ok",
        "profile": {
            "snapshot_date": p.get("snapshot_date"),
            "source": p.get("source"),
            "good_version": p.get("good_version"),
            "kamera_version": p.get("kamera_version"),
            "sha256": p.get("sha256"),
            "counts": p.get("counts", {}),
            "unresolved": p.get("unresolved_character_keys", []),
            "provenance_note": p.get("provenance_note"),
        },
    })


def cmd_overview() -> None:
    try:
        cur = load_current()
    except FileNotFoundError:
        _emit({"status": "empty"})
        return
    _emit({"status": "ok", "overview": build_overview(cur)})


def cmd_import(path: str) -> None:
    res = import_good(path)
    v = res["validation"]
    _emit({
        "status": "ok",
        "import": {
            "sha256": res["sha256"],
            "snapshot": res["snapshot"],
            "idempotent_skip": res["idempotent_skip"],
            "counts": res["counts"],
            "validation": v["counts_by_severity"],
            "unresolved": v["unresolved_characters"],
            "duplicate_weapon_ids": bool(v["duplicate_weapon_ids"]),
        },
    })


def main(argv: list[str]) -> int:
    if not argv:
        _emit({"error": "usage: account_ipc <profile|overview|import-good CHEMIN>"})
        return 2
    cmd = argv[0]
    try:
        if cmd == "profile":
            cmd_profile()
        elif cmd == "overview":
            cmd_overview()
        elif cmd == "import-good":
            if len(argv) < 2:
                _emit({"error": "chemin requis"})
                return 2
            cmd_import(argv[1])
        else:
            _emit({"error": f"commande inconnue: {cmd}"})
            return 2
    except Exception as exc:  # noqa: BLE001 — surfacer proprement au frontend, sans masquer
        _emit({"error": str(exc), "type": type(exc).__name__})
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
