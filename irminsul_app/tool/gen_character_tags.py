# Genere assets/data/character_tags.json : ce que CHAQUE perso sait faire.
# Sans ca, un optimiseur d'equipes ne peut pas raisonner (il ne saurait pas
# qui soigne, qui applique un element hors terrain, qui shred la RES...).
#
# Source : descriptions FR officielles de genshin-db (data/sources/genshin-db),
# detectees par mots-cles, PUIS corrigees par OVERRIDES explicites (un mot-cle
# se trompe parfois : on ne cache pas la correction, on l'ecrit).
#
#   python tool/gen_character_tags.py
import json
import re
import sys
import unicodedata
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parent
TALENTS = ROOT / "data/sources/genshin-db/src/data/French/talents"

# --- roles detectes par mots-cles dans les descriptions de talents ----------
# (chaque motif est volontairement large : les faux positifs sont rattrapes
#  par OVERRIDES, les faux negatifs aussi.)
PATTERNS = {
    "heal": r"soigne|rend des PV|restaure des PV|régénère des PV|redonne des PV|soins",
    "shield": r"bouclier",
    "atk_buff": r"(augmente|bonus)[^.]{0,60}ATQ|ATQ[^.]{0,40}augment",
    "dmg_buff": r"bonus de DGT|DGT[^.]{0,40}augment[^.]{0,40}%",
    "res_shred": r"RÉS[^.]{0,60}(réduit|diminue)|réduit[^.]{0,60}RÉS",
    "def_shred": r"DÉF[^.]{0,60}(réduit|diminue)|ignore[^.]{0,30}DÉF",
    "em_buff": r"maîtrise élémentaire[^.]{0,40}(augment|bonus)",
    "energy": r"régénère de l'énergie|particules? élémentaires?|énergie élémentaire",
    "offfield": r"hors[- ]terrain|hors du terrain|même si le personnage n'est pas",
    "crowd": r"attire|aspire|regroupe les ennemis",
    "interrupt": r"résistance aux interruptions",
    "nightsoul": r"nocturme|Nightsoul|âme nocturne",
}

# --- corrections explicites (mot-cle insuffisant ou trompeur) ---------------
# format : "GOODKey": {"add": [...], "remove": [...], "carry": bool}
OVERRIDES = {
    "Bennett": {"add": ["heal", "atk_buff", "energy"], "carry": False},
    "Xiangling": {"add": ["offfield"], "carry": False},
    "Xingqiu": {"add": ["offfield"], "carry": False},
    "Fischl": {"add": ["offfield"], "carry": False},
    "Zhongli": {"add": ["shield", "res_shred"], "carry": False},
    "Kazuha": {"add": ["dmg_buff", "crowd", "res_shred"], "carry": False},
    "Sucrose": {"add": ["em_buff", "crowd", "res_shred"], "carry": False},
    "Citlali": {"add": ["shield", "res_shred", "em_buff"], "carry": False},
    "Xilonen": {"add": ["res_shred", "heal", "nightsoul"], "carry": False},
    "Iansan": {"add": ["atk_buff", "nightsoul"], "carry": False},
    "Furina": {"add": ["dmg_buff", "offfield"], "carry": False},
    "Nahida": {"add": ["em_buff", "offfield"], "carry": False},
    "Chevreuse": {"add": ["heal", "atk_buff", "res_shred"], "carry": False},
    "Mavuika": {"add": ["nightsoul"], "carry": True},
    "Skirk": {"carry": True},
    "HuTao": {"carry": True},
    "Ayaka": {"carry": True},
    "Neuvillette": {"carry": True},
    "RaidenShogun": {"add": ["energy"], "carry": True},
    "Arlecchino": {"carry": True},
    "Mualani": {"add": ["nightsoul"], "carry": True},
    "Xiao": {"carry": True},
    "Nilou": {"carry": False},
    "Columbina": {"carry": True},
    "Flins": {"carry": True},
    "Lauma": {"add": ["em_buff", "offfield"], "carry": False},
    "Ineffa": {"add": ["atk_buff"], "carry": False},
    "Nicole": {"carry": True},
    "Aino": {"add": ["heal"], "carry": False},
    "Ororon": {"add": ["offfield", "nightsoul"], "carry": False},
    "Durin": {"carry": True},
}

# carries « connus » (DPS principal credible) — complete l'heuristique 5*
KNOWN_CARRIES = {
    "Mavuika", "Skirk", "HuTao", "Ayaka", "Neuvillette", "RaidenShogun",
    "Arlecchino", "Mualani", "Xiao", "Columbina", "Flins", "Nicole",
    "Diluc", "Eula", "Ganyu", "Itto", "Yoimiya", "Alhaitham", "Cyno",
    "Wriothesley", "Navia", "Clorinde", "Lyney", "Chasca", "Kinich",
    "Varesa", "Keqing", "Tartaglia", "Noelle", "Razor", "Sethos",
    "Wanderer", "Yanfei", "Klee", "Xinyan", "Heizou", "Ifa", "Lohen",
    "Zibai", "Linnea", "Sandrone", "Nefer", "Illuga",
}

# reactions rendues possibles par un element (pour le scoring de contenu)
ELEMENT_REACTIONS = {
    "pyro": ["vaporize", "melt", "overloaded", "burning", "burgeon"],
    "hydro": ["vaporize", "electro-charged", "frozen", "bloom"],
    "electro": ["overloaded", "electro-charged", "superconduct", "aggravate",
                "hyperbloom", "quicken", "lunar-charged"],
    "cryo": ["melt", "frozen", "superconduct", "stellar-conduct"],
    "dendro": ["bloom", "burning", "quicken", "aggravate", "spread",
               "hyperbloom", "burgeon", "lunar-bloom"],
    "anemo": ["swirl"],
    "geo": ["crystallize"],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def talent_text(good_key: str, name: str) -> str:
    """Concatene les descriptions de talents/passifs d'un perso."""
    for cand in {norm(good_key), norm(name)}:
        p = TALENTS / f"{cand}.json"
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            out = []
            for k, v in d.items():
                if isinstance(v, dict):
                    out.append(v.get("descriptionRaw") or v.get("description") or "")
            return "\n".join(out)
    return ""


def main() -> int:
    full = json.loads(
        (APP / "assets/data/characters_full.json").read_text(encoding="utf-8"))
    out, no_source = {}, []
    for c in full["characters"]:
        text = talent_text(c["good"], c["name"])
        if not text:
            no_source.append(c["name"])
        tags = {k for k, pat in PATTERNS.items()
                if re.search(pat, text, re.I)}
        ov = OVERRIDES.get(c["good"], {})
        tags |= set(ov.get("add", []))
        tags -= set(ov.get("remove", []))
        carry = ov.get("carry")
        if carry is None:
            carry = c["good"] in KNOWN_CARRIES
        out[c["good"]] = {
            "element": c["element"],
            "rarity": c["rarity"],
            "weapon": c["weaponType"],
            "tags": sorted(tags),
            "carry": bool(carry),
            "reactions": ELEMENT_REACTIONS.get(c["element"], []),
            "sourced": bool(text),
        }
    (APP / "assets/data/character_tags.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    n_tagged = sum(1 for v in out.values() if v["tags"])
    print(f"OK {len(out)} persos · {n_tagged} avec au moins un role detecte · "
          f"{sum(1 for v in out.values() if v['carry'])} carries")
    if no_source:
        print(f"ATTENTION descriptions introuvables ({len(no_source)}) : "
              + ", ".join(no_source[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
