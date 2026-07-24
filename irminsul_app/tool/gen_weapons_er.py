"""Génère assets/data/weapons_er.json : ER% exacte par niveau (1..90) pour
chaque arme à sous-stat Recharge d'énergie. Source : genshin-db stats+curve
(données du jeu). Clé = clé GOOD (nom EN sans espaces), ex. FavoniusSword.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "sources" / "genshin-db" / "src" / "data"
OUT = Path(__file__).resolve().parents[1] / "assets" / "data" / "weapons_er.json"


def good_key(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


def main() -> None:
    stats = json.loads((SRC / "stats" / "weapons.json").read_text(encoding="utf-8"))
    curves = json.loads((SRC / "curve" / "weapons.json").read_text(encoding="utf-8"))

    out: dict[str, list[float]] = {}
    for stem, s in stats.items():
        if s.get("specialized") != "FIGHT_PROP_CHARGE_EFFICIENCY":
            continue
        base = s["base"]["specialized"]
        curve_name = s["curve"]["specialized"]
        en = SRC / "English" / "weapons" / f"{stem}.json"
        if not en.exists():
            continue
        name = json.loads(en.read_text(encoding="utf-8"))["name"]
        # curve/weapons.json : {"<niveau>": {"<courbe>": mult, ...}, ...}
        vals: list[float] = []
        ok = True
        for lvl in range(1, 91):
            level_map = curves.get(str(lvl))
            mult = level_map.get(curve_name) if level_map else None
            if mult is None:
                ok = False
                break
            vals.append(round(base * mult * 100, 2))
        if ok:
            out[good_key(name)] = vals

    OUT.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    fav = out.get("FavoniusSword", [])
    sky = out.get("SkywardBlade", [])
    sac = out.get("SacrificialSword", [])
    print(f"OK {len(out)} armes ER -> {OUT.name}")
    print(f"verif FavoniusSword lvl90={fav[-1] if fav else '?'} (attendu 61.3)")
    print(f"SkywardBlade lvl60={sky[59] if sky else '?'} | SacrificialSword lvl70={sac[69] if sac else '?'}")


if __name__ == "__main__":
    main()
