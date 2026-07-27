"""Extrait d'un datamine PUBLIC les données exactes d'un personnage.

Sert à implémenter dans gcsim les persos que la communauté n'a pas encore
codés (Sandrone, Zibai, Lohen, Linnea, Illuga, Nefer…). On ne devine aucun
multiplicateur : ils viennent des tables du jeu.

Source : https://github.com/iam-akuzihs/excel (branche `live`), le même dépôt
que le pipeline officiel de gcsim. Les fichiers sont mis en cache dans
data/sources/datamine/ (gitignoré).

    python tool/datamine.py Sandrone            # résumé lisible
    python tool/datamine.py Sandrone --json out.json
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parent
CACHE = ROOT / "data/sources/datamine"
BASE = "https://raw.githubusercontent.com/iam-akuzihs/excel/live/ExcelBinOutput"

FILES = [
    "AvatarExcelConfigData",
    "AvatarSkillDepotExcelConfigData",
    "AvatarSkillExcelConfigData",
    "ProudSkillExcelConfigData",
    "AvatarPromoteExcelConfigData",
    "AvatarCurveExcelConfigData",
]


def load(name: str) -> list | dict:
    """Télécharge une table du datamine (une seule fois) et la retourne."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{name}.json"
    if not p.exists():
        url = f"{BASE}/{name}.json"
        print(f"  téléchargement {name}…", file=sys.stderr)
        with urllib.request.urlopen(url, timeout=180) as r:
            p.write_bytes(r.read())
    return json.loads(p.read_text(encoding="utf-8"))


def avatar_id(name: str) -> int:
    """Identifiant du perso, lu dans genshin-db local (pas de TextMap à charger)."""
    p = ROOT / "data/sources/genshin-db/src/data/English/characters"
    f = p / f"{name.lower().replace(' ', '')}.json"
    if not f.exists():
        raise SystemExit(f"perso inconnu de genshin-db : {name}")
    return json.loads(f.read_text(encoding="utf-8"))["id"]


def by_id(rows: list, key: str) -> dict:
    return {r[key]: r for r in rows if key in r}


def extract(name: str) -> dict:
    aid = avatar_id(name)
    avatars = by_id(load("AvatarExcelConfigData"), "id")
    av = avatars.get(aid)
    if av is None:
        raise SystemExit(f"{name} (id {aid}) absent du datamine")

    depots = by_id(load("AvatarSkillDepotExcelConfigData"), "id")
    skills = by_id(load("AvatarSkillExcelConfigData"), "id")
    prouds = load("ProudSkillExcelConfigData")
    proud_by_group: dict[int, list] = {}
    for r in prouds:
        proud_by_group.setdefault(r.get("proudSkillGroupId"), []).append(r)
    for v in proud_by_group.values():
        v.sort(key=lambda r: r.get("level", 0))

    depot = depots.get(av.get("skillDepotId"), {})
    out: dict = {
        "name": name,
        "avatarId": aid,
        "quality": av.get("qualityType"),
        "weapon": av.get("weaponType"),
        "baseHp": av.get("hpBase"),
        "baseAtk": av.get("attackBase"),
        "baseDef": av.get("defenseBase"),
        "growCurves": av.get("propGrowCurves"),
        "promoteId": av.get("avatarPromoteId"),
        "talents": {},
    }

    def add(role: str, skill_id: int) -> None:
        sk = skills.get(skill_id)
        if not sk:
            return
        group = sk.get("proudSkillGroupId")
        levels = proud_by_group.get(group, [])
        out["talents"][role] = {
            "skillId": skill_id,
            "cd": sk.get("cdTime"),
            "energy": sk.get("costElemVal"),
            "costElement": sk.get("costElemType"),
            "maxCharges": sk.get("maxChargeNum"),
            # paramList par niveau de talent (1..15) : les multiplicateurs
            "params": [r.get("paramList", []) for r in levels],
            "paramDescs": levels[0].get("paramDescList", []) if levels else [],
        }

    ids = [s for s in depot.get("skills", []) if s]
    if ids:
        add("normal", ids[0])
    if len(ids) > 1:
        add("skill", ids[1])
    if depot.get("energySkill"):
        add("burst", depot["energySkill"])

    out["constellations"] = depot.get("talents", [])
    out["passives"] = [
        p.get("proudSkillGroupId")
        for p in depot.get("inherentProudSkillOpens", [])
        if p.get("proudSkillGroupId")
    ]
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    name = sys.argv[1]
    data = extract(name)
    if "--json" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--json") + 1])
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        print(f"-> {out}")
        return 0

    print(f"=== {data['name']} (id {data['avatarId']}) ===")
    print(f"  {data['quality']} · {data['weapon']} · "
          f"HP {data['baseHp']:.1f} / ATQ {data['baseAtk']:.1f} / "
          f"DÉF {data['baseDef']:.1f}")
    for role, t in data["talents"].items():
        lv = t["params"][9] if len(t["params"]) > 9 else (
            t["params"][-1] if t["params"] else [])
        useful = [round(x, 4) for x in lv[:12] if x]
        print(f"  {role:7s} CD {t['cd']}s · énergie {t['energy']} · "
              f"{len(t['params'])} niveaux")
        print(f"          params niv.10 : {useful}")
    print(f"  constellations : {len(data['constellations'])} · "
          f"passifs : {len(data['passives'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
