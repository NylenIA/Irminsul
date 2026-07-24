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


def mat_entries(costs: dict, fr_icon: dict[str, str]) -> list[dict]:
    """Agrège {nom -> quantité totale} en gardant l'ordre d'apparition."""
    order: list[str] = []
    totals: dict[str, int] = {}
    for items in costs.values():
        for it in items:
            n = it.get("name", "")
            if not n or n == "Mora":
                continue
            if n not in totals:
                order.append(n)
                totals[n] = 0
            totals[n] += int(it.get("count", 0))
    return [
        {"n": n, "q": totals[n], "i": fr_icon.get(n, "")} for n in order
    ]


def main() -> None:
    img_chars = load(SRC / "image" / "characters.json")
    img_talents = load(SRC / "image" / "talents.json")
    img_cons = load(SRC / "image" / "constellations.json")
    img_mats = load(SRC / "image" / "materials.json")

    # nom FR de matériau -> icône (UI_ItemIcon_…)
    fr_icon: dict[str, str] = {}
    for mf in (SRC / "French" / "materials").glob("*.json"):
        m = load(mf)
        icon = (img_mats.get(mf.stem) or {}).get("filename_icon", "")
        if m.get("name") and icon:
            fr_icon[m["name"]] = icon

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

        # ---- matériaux (avec quantités totales + icônes) ----
        asc = mat_entries(c.get("costs", {}), fr_icon)
        tal: list[dict] = []
        if tfile.exists():
            tal = mat_entries(load(tfile).get("costs", {}), fr_icon)

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
            "splash": (img_chars.get(cid) or {}).get("filename_gachaSplash", ""),
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
