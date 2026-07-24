# Genere une config gcsim depuis un GOOD reel (miroir de la future logique Dart).
# Usage : python tool/gen_gcsim_config.py <GOOD.json> <team_id> [out.txt]
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]

# GOOD key -> cle gcsim (exceptions aux minuscules simples)
CHAR_MAP = {
    "RaidenShogun": "raiden",
    "KaedeharaKazuha": "kazuha",
    "KamisatoAyaka": "ayaka",
    "KamisatoAyato": "ayato",
    "SangonomiyaKokomi": "kokomi",
    "KukiShinobu": "kuki",
    "YaeMiko": "yaemiko",
    "AratakiItto": "itto",
    "KujouSara": "sara",
    "ShikanoinHeizou": "heizou",
    "Tartaglia": "tartaglia",
    "HuTao": "hutao",
    "YumemizukiMizuki": "mizuki",
}

# maxLvl par palier d'ascension (persos ET armes)
ASC_MAX = [20, 40, 50, 60, 70, 80, 90]

# stat GOOD -> (cle gcsim, est_un_pourcentage)
STAT_MAP = {
    "hp": ("hp", False), "hp_": ("hp%", True),
    "atk": ("atk", False), "atk_": ("atk%", True),
    "def": ("def", False), "def_": ("def%", True),
    "eleMas": ("em", False), "enerRech_": ("er", True),
    "critRate_": ("cr", True), "critDMG_": ("cd", True),
    "heal_": ("heal", True), "physical_dmg_": ("phys%", True),
    "pyro_dmg_": ("pyro%", True), "hydro_dmg_": ("hydro%", True),
    "cryo_dmg_": ("cryo%", True), "electro_dmg_": ("electro%", True),
    "anemo_dmg_": ("anemo%", True), "geo_dmg_": ("geo%", True),
    "dendro_dmg_": ("dendro%", True),
}

# main stat max (5*, +20) et (4*, +16)
MAIN_MAX_5 = {
    "hp": 4780, "atk": 311.5, "hp_": 46.6, "atk_": 46.6, "def_": 58.3,
    "eleMas": 186.5, "enerRech_": 51.8, "critRate_": 31.1, "critDMG_": 62.2,
    "heal_": 35.9, "physical_dmg_": 58.3, "pyro_dmg_": 46.6,
    "hydro_dmg_": 46.6, "cryo_dmg_": 46.6, "electro_dmg_": 46.6,
    "anemo_dmg_": 46.6, "geo_dmg_": 46.6, "dendro_dmg_": 46.6,
}
MAIN_MAX_4 = {
    "hp": 3571, "atk": 232, "hp_": 34.8, "atk_": 34.8, "def_": 43.5,
    "eleMas": 139.3, "enerRech_": 38.7, "critRate_": 23.3, "critDMG_": 46.6,
    "heal_": 26.8, "physical_dmg_": 43.5, "pyro_dmg_": 34.8,
    "hydro_dmg_": 34.8, "cryo_dmg_": 34.8, "electro_dmg_": 34.8,
    "anemo_dmg_": 34.8, "geo_dmg_": 34.8, "dendro_dmg_": 34.8,
}


def main_stat_value(key, rarity, level):
    table = MAIN_MAX_5 if rarity >= 5 else MAIN_MAX_4
    mx = table.get(key)
    if mx is None:
        return None
    max_lvl = 20 if rarity >= 5 else 16
    lvl = max(0, min(level, max_lvl))
    # progression lineaire : base (niv 0) = 15 % du max
    return mx * (0.15 + 0.85 * lvl / max_lvl)


def gcsim_char(good_key):
    return CHAR_MAP.get(good_key, good_key.lower())


def build_config(good, team_good_keys, rotation, options):
    chars = {c["key"]: c for c in good.get("characters", [])}
    lines = []
    for gk in team_good_keys:
        c = chars.get(gk)
        if c is None:
            raise SystemExit(f"perso absent de la box: {gk}")
        name = gcsim_char(gk)
        max_lvl = ASC_MAX[min(int(c.get("ascension", 6)), 6)]
        t = c.get("talent", {}) or {}
        lines.append(
            f'{name} char lvl={c.get("level", 90)}/{max_lvl} '
            f'cons={c.get("constellation", 0)} '
            f'talent={t.get("auto", 6)},{t.get("skill", 6)},{t.get("burst", 6)};'
        )
        # arme equipee
        w = next((x for x in good.get("weapons", []) if x.get("location") == gk),
                 None)
        if w is None:
            raise SystemExit(f"pas d'arme equipee: {gk}")
        wmax = ASC_MAX[min(int(w.get("ascension", 6)), 6)]
        lines.append(
            f'{name} add weapon="{w["key"].lower()}" '
            f'refine={w.get("refinement", 1)} lvl={w.get("level", 90)}/{wmax};'
        )
        # artefacts equipes : sets + stats agregees
        arts = [a for a in good.get("artifacts", []) if a.get("location") == gk]
        set_counts = {}
        totals = {}
        for a in arts:
            set_counts[a["setKey"]] = set_counts.get(a["setKey"], 0) + 1
            mv = main_stat_value(a.get("mainStatKey", ""),
                                 a.get("rarity", 5), a.get("level", 0))
            if mv is not None:
                totals[a["mainStatKey"]] = totals.get(a["mainStatKey"], 0) + mv
            for s in a.get("substats", []):
                k, v = s.get("key"), s.get("value", 0) or 0
                if k:
                    totals[k] = totals.get(k, 0) + v
        for sk, n in sorted(set_counts.items()):
            if n >= 2:
                lines.append(
                    f'{name} add set="{sk.lower()}" count={4 if n >= 4 else 2};')
        parts = []
        for k in sorted(totals):
            m = STAT_MAP.get(k)
            if not m:
                continue
            key, pct = m
            v = totals[k] / 100 if pct else totals[k]
            parts.append(f"{key}={v:.4f}" if pct else f"{key}={v:.1f}")
        if parts:
            lines.append(f'{name} add stats {" ".join(parts)};')
        lines.append("")
    first = gcsim_char(team_good_keys[0])
    lines.append(f"active {first};")
    lines.append(options.strip())
    lines.append("")
    lines.append(rotation.strip())
    return "\n".join(lines) + "\n"


TEAMS = {
    # Raiden National — rotation séquentielle classique, en boucle
    "raiden-national": {
        "chars": ["Bennett", "Xiangling", "Xingqiu", "RaidenShogun"],
        "rotation": """
while 1 {
    bennett skill, burst;
    xiangling burst, skill;
    xingqiu skill, burst;
    raiden skill;
    raiden burst;
    raiden attack:8;
    raiden skill;
    bennett attack, skill;
    xiangling attack, skill;
    xingqiu attack:2;
}
""",
    },
    # Nahida Hyperbloom
    "nahida-hb": {
        "chars": ["Nahida", "Furina", "Xingqiu", "RaidenShogun"],
        "rotation": """
while 1 {
    nahida skill, burst;
    furina skill;
    xingqiu skill, burst;
    raiden skill;
    raiden attack:10;
    nahida skill;
    furina attack:2;
    xingqiu attack:2;
    raiden attack:8;
}
""",
    },
}

TEAMS["fischl-taser"] = {
    "chars": ["Fischl", "Beidou", "Xingqiu", "Sucrose"],
    "rotation": """
while 1 {
    fischl skill;
    beidou skill, burst;
    xingqiu skill, burst;
    sucrose skill;
    sucrose attack:6;
    fischl burst;
    sucrose attack:6;
    sucrose skill;
    sucrose attack:4;
}
""",
}
TEAMS["furina-mono"] = {
    "chars": ["Furina", "Barbara", "Fischl", "Beidou"],
    "rotation": """
while 1 {
    furina skill;
    fischl skill;
    beidou skill, burst;
    barbara skill;
    furina burst;
    furina attack:6;
    fischl burst;
    furina attack:8;
}
""",
}

OPTIONS = """
options iteration=100 duration=90 swap_delay=12;
target lvl=100 resist=0.1;
energy every interval=480,720 amount=1;
"""

if __name__ == "__main__":
    good = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    team = TEAMS[sys.argv[2]]
    cfg = build_config(good, team["chars"], team["rotation"], OPTIONS)
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "build_gcsim.txt"
    out.write_text(cfg, encoding="utf-8")
    print(f"OK -> {out}")
    print(cfg[:600])
