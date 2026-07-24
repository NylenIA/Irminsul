"""Génère assets/data/characters_full.json depuis genshin-db (données du jeu, FR).

Source : data/sources/genshin-db/src/data/{French,image}/ — 120 personnages.
Zéro donnée inventée : noms, descriptions, aptitudes, constellations et
matériaux viennent des fichiers du jeu. Les builds curés restent dans
characters.json (séparés, étiquetés).

Usage : python tool/gen_characters_db.py   (depuis irminsul_app/)
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # racine du dépôt
SRC = ROOT / "data" / "sources" / "genshin-db" / "src" / "data"
OUT = Path(__file__).resolve().parents[1] / "assets" / "data" / "characters_full.json"

ELEMENT_MAP = {
    "pyro": "pyro", "hydro": "hydro", "électro": "electro", "electro": "electro",
    "cryo": "cryo", "anémo": "anemo", "anemo": "anemo", "géo": "geo", "geo": "geo",
    "dendro": "dendro", "aucun": "none", "none": "none",
}

TAG_RE = re.compile(r"<[^>]+>")


def clean(text: str | None) -> str:
    if not text:
        return ""
    return TAG_RE.sub("", text).strip()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mat_names(costs: dict) -> list[str]:
    seen: list[str] = []
    for items in costs.values():
        for it in items:
            n = it.get("name", "")
            if n and n != "Mora" and n not in seen:
                seen.append(n)
    return seen


def main() -> None:
    img_chars = load(SRC / "image" / "characters.json")
    img_talents = load(SRC / "image" / "talents.json")
    img_cons = load(SRC / "image" / "constellations.json")

    chars_dir = SRC / "French" / "characters"
    talents_dir = SRC / "French" / "talents"
    cons_dir = SRC / "French" / "constellations"

    out: list[dict] = []
    skipped: list[str] = []
    for f in sorted(chars_dir.glob("*.json")):
        cid = f.stem
        c = load(f)
        element = ELEMENT_MAP.get((c.get("elementText") or "").lower(), "none")
        icon = (img_chars.get(cid) or {}).get("filename_icon", "")
        if not icon:
            skipped.append(cid)
            continue

        # ---- aptitudes ----
        talents: list[dict] = []
        tfile = talents_dir / f"{cid}.json"
        if tfile.exists():
            t = load(tfile)
            timg = img_talents.get(cid) or {}
            slots = [
                ("combat1", "Attaque normale"), ("combat2", "Compétence (E)"),
                ("combat3", "Ultime (Q)"), ("combatsp", "Sprint spécial"),
                ("passive1", "Passif — Élévation 1"),
                ("passive2", "Passif — Élévation 4"),
                ("passive3", "Passif — Exploration"), ("passive4", "Passif"),
            ]
            for key, label in slots:
                node = t.get(key)
                if not node:
                    continue
                talents.append({
                    "slot": label,
                    "name": clean(node.get("name")),
                    "icon": timg.get(f"filename_{key}", ""),
                    "desc": clean(node.get("description")),
                })

        # ---- constellations ----
        cons: list[dict] = []
        kfile = cons_dir / f"{cid}.json"
        if kfile.exists():
            k = load(kfile)
            kimg = img_cons.get(cid) or {}
            for i in range(1, 7):
                node = k.get(f"c{i}")
                if not node:
                    continue
                cons.append({
                    "n": i,
                    "name": clean(node.get("name")),
                    "icon": kimg.get(f"filename_c{i}", ""),
                    "desc": clean(node.get("description")),
                })

        # ---- matériaux ----
        asc = mat_names(c.get("costs", {}))
        tal: list[str] = []
        if tfile.exists():
            tal = mat_names(load(tfile).get("costs", {}))

        out.append({
            "id": cid,
            "name": clean(c.get("name")),
            "title": clean(c.get("title")),
            "element": element,
            "rarity": int(c.get("rarity") or 4),
            "weaponType": clean(c.get("weaponText")),
            "region": clean(c.get("region")),
            "description": clean(c.get("description"))[:400],
            "icon": icon,
            "talents": talents,
            "cons": cons,
            "matAscension": asc,
            "matTalents": tal,
        })

    payload = {
        "generatedOn": date.today().isoformat(),
        "source": "genshin-db (données du jeu, FR)",
        "count": len(out),
        "characters": out,
    }
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    size_kb = OUT.stat().st_size // 1024
    print(f"OK {len(out)} persos -> {OUT.name} ({size_kb} Ko) ; ignorés: {skipped}")


if __name__ == "__main__":
    main()
