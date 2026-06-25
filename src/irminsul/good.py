from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import project_root


def inspect_good_export(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = project_root() / file_path
    if not file_path.exists():
        raise FileNotFoundError(f"Export GOOD introuvable : {file_path}")
    if file_path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("Export GOOD trop volumineux (>100 Mo)")

    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if payload.get("format") != "GOOD":
        raise ValueError("Le fichier n'est pas un export GOOD valide")

    characters = payload.get("characters") or []
    weapons = payload.get("weapons") or []
    artifacts = payload.get("artifacts") or []
    materials = payload.get("materials") or {}

    artifact_sets: dict[str, int] = {}
    equipped_artifacts = 0
    for artifact in artifacts:
        set_key = str(artifact.get("setKey", "unknown"))
        artifact_sets[set_key] = artifact_sets.get(set_key, 0) + 1
        if artifact.get("location"):
            equipped_artifacts += 1

    character_keys = sorted(
        str(character.get("key", "unknown")) for character in characters
    )
    weapon_keys: dict[str, int] = {}
    for weapon in weapons:
        key = str(weapon.get("key", "unknown"))
        weapon_keys[key] = weapon_keys.get(key, 0) + 1

    return {
        "path": str(file_path),
        "format": payload.get("format"),
        "version": payload.get("version"),
        "source": payload.get("source"),
        "counts": {
            "characters": len(characters),
            "weapons": len(weapons),
            "artifacts": len(artifacts),
            "equipped_artifacts": equipped_artifacts,
            "materials": len(materials),
        },
        "characters": character_keys,
        "weapon_inventory": dict(sorted(weapon_keys.items())),
        "artifact_sets": dict(sorted(artifact_sets.items(), key=lambda item: (-item[1], item[0]))),
        "raw_keys": sorted(payload.keys()),
    }
