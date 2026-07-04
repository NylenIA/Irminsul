"""Pont « moteur compte » : fonctions *_payload() renvoyant des dicts JSON-ables.

Réutilisées par : le CLI argv (`python -m irminsul.account_ipc <cmd>`, pratique en
dev/tests) et par le **sidecar** stdin/stdout (`irminsul.sidecar`). Aucune donnée
factice : si aucun compte n'est importé → `{"status": "empty"}`.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .account import build_overview, import_good, load_current


def profile_payload() -> dict[str, Any]:
    try:
        cur = load_current()
    except FileNotFoundError:
        return {"status": "empty", "message": "Aucun compte importé."}
    p = cur["account-profile"]
    return {
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
    }


def overview_payload() -> dict[str, Any]:
    try:
        cur = load_current()
    except FileNotFoundError:
        return {"status": "empty"}
    return {"status": "ok", "overview": build_overview(cur)}


def roster_payload() -> dict[str, Any]:
    try:
        cur = load_current()
    except FileNotFoundError:
        return {"status": "empty"}
    chars = cur["characters"]["characters"]
    weapons = cur["weapons"]["weapons"]
    arts = cur["artifacts"]["artifacts"]

    character_list = []
    for key, c in sorted(chars.items()):
        wid = c.get("weapon")
        w = weapons.get(wid) if wid else None
        art_ids = [a for a in (c.get("artifacts") or {}).values() if a in arts]
        set_counts: dict[str, int] = {}
        for a in art_ids:
            sk = arts[a]["setKey"]
            set_counts[sk] = set_counts.get(sk, 0) + 1
        dominant = max(set_counts.items(), key=lambda x: x[1])[0] if set_counts else None
        character_list.append({
            "key": key, "level": c.get("level"), "ascension": c.get("ascension"),
            "constellation": c.get("constellation"), "talents": c.get("talents") or {},
            "weapon": ({"key": w["key"], "level": w["level"], "refinement": w["refinement"]}
                       if w else None),
            "artifacts": len(art_ids), "dominant_set": dominant,
        })

    weapon_list = sorted(
        ({"key": w["key"], "level": w["level"], "refinement": w["refinement"],
          "location": w["location"]} for w in weapons.values()),
        key=lambda x: (x["location"] is None, x["key"]),
    )

    set_summary: dict[str, dict[str, int]] = {}
    for a in arts.values():
        s = set_summary.setdefault(a["setKey"], {"total": 0, "equipped": 0})
        s["total"] += 1
        if a["location"]:
            s["equipped"] += 1
    artifact_sets = [{"setKey": k, **v} for k, v in
                     sorted(set_summary.items(), key=lambda x: -x[1]["total"])]

    return {"status": "ok", "roster": {
        "counts": cur["account-profile"]["counts"],
        "characters": character_list, "weapons": weapon_list, "artifact_sets": artifact_sets,
    }}


def import_payload(path: str) -> dict[str, Any]:
    res = import_good(path)
    v = res["validation"]
    return {"status": "ok", "import": {
        "sha256": res["sha256"], "snapshot": res["snapshot"],
        "idempotent_skip": res["idempotent_skip"], "counts": res["counts"],
        "validation": v["counts_by_severity"], "unresolved": v["unresolved_characters"],
        "duplicate_weapon_ids": bool(v["duplicate_weapon_ids"]),
    }}


# Table de dispatch partagée (CLI + sidecar).
def dispatch(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or {}
    if method == "profile":
        return profile_payload()
    if method == "overview":
        return overview_payload()
    if method == "roster":
        return roster_payload()
    if method == "import-good":
        path = params.get("path")
        if not path:
            raise ValueError("paramètre 'path' requis")
        return import_payload(str(path))
    if method == "mechanics":
        from .quickcalc import mechanics_payload
        return mechanics_payload()
    if method == "quick-calc":
        from .quickcalc import quickcalc_payload
        return quickcalc_payload(params)
    if method == "characters":
        from .charstats import characters_payload
        return characters_payload()
    if method == "character-stats":
        from .charstats import character_payload
        key = params.get("key")
        if not key:
            raise ValueError("paramètre 'key' requis")
        return character_payload(str(key))
    raise ValueError(f"méthode inconnue: {method}")


def main(argv: list[str]) -> int:
    """CLI argv (dev/tests) : `account_ipc <profile|overview|roster|import-good CHEMIN>`."""
    if not argv:
        sys.stdout.write(json.dumps({"error": "usage: <profile|overview|roster|import-good CHEMIN>"}))
        return 2
    method = argv[0]
    params = {"path": argv[1]} if method == "import-good" and len(argv) > 1 else {}
    try:
        sys.stdout.write(json.dumps(dispatch(method, params), ensure_ascii=False, default=str))
    except ValueError as exc:
        sys.stdout.write(json.dumps({"error": str(exc)}))
        return 2
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps({"error": str(exc), "type": type(exc).__name__}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
