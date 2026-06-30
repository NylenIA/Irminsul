#!/usr/bin/env python3
"""Génère apps/web/src/lib/characters.json depuis la source LOCALE genshin-db.

Données réelles (nom, élément, rareté, type d'arme) — aucune invention. Reproductible.
Source gitignorée (data/sources/genshin-db) ; le JSON généré (données publiques) est committé.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sources" / "genshin-db" / "src" / "data" / "English" / "characters"
OUT = ROOT / "apps" / "web" / "src" / "lib" / "characters.json"

# Voyageur multi-élément : on garde 'aether' comme entrée générique unique.
SKIP = {"lumine"}


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Source genshin-db introuvable : {SRC}")
    out: list[dict[str, object]] = []
    for f in sorted(SRC.glob("*.json")):
        if f.stem in SKIP:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        name = d.get("name")
        if not name:
            continue
        out.append(
            {
                "id": f.stem,
                "name": name,
                "element": d.get("elementText") or None,
                "rarity": d.get("rarity") or None,
                "weapon": d.get("weaponText") or None,
                "source": "local-data",
            }
        )
    out.sort(key=lambda c: str(c["name"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(out)} personnages -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
