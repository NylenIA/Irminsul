"""Statistiques de BASE des personnages (PV/ATQ/DÉF par niveau + ascension).

Principe d'honnêteté : on calcule **exactement** les personnages présents dans la
source locale (genshin-db, theBowja/genshin-db), versionnée et sourcée ; tout le
reste est signalé **explicitement** comme non pris en charge (jamais inventé).

Formule (jeu / KQM) :
    stat(niveau, ascension) = base × courbe[niveau] + promotion[ascension]

Les données sont *extraites* depuis `data/sources/genshin-db/src/data/{curve,stats}`
(gitignoré) vers un fichier **committé** `data/mechanics/character-basestats.json`
(provenance : commit + date + formule + confiance). Ce fichier voyage AVEC le moteur
(embarqué dans le sidecar PyInstaller), exactement comme le registre des mécaniques.

Le module *runtime* (ce fichier) ne lit que le JSON committé. L'extraction depuis la
source brute vit dans `tools/extract_basestats.py` et appelle `extract_from_genshin_db`.
"""

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import project_root

# --- Bornes du jeu (à ce patch) : niveaux 1..90, ascensions 0..6 (7 paliers). --- #
MIN_LEVEL = 1
MAX_LEVEL = 90
MAX_ASCENSION = 6

# Plage de niveau valide pour chaque palier d'ascension (mécanique du jeu : ascender
# débloque le palier suivant au même niveau). Sert à REJETER les paires impossibles
# (ex. niveau 90 à l'ascension 0) au lieu de calculer une valeur fausse.
ASCENSION_LEVEL_FLOOR = (1, 20, 40, 50, 60, 70, 80)
ASCENSION_LEVEL_CAP = (20, 40, 50, 60, 70, 80, 90)

# Variantes de Voyageur partageant les stats de base (= aether, vérifié == lumine).
_TRAVELER_ELEMENTS = {"anemo", "geo", "electro", "dendro", "hydro", "pyro", "cryo"}

# Stat d'ascension genshin-db (FIGHT_PROP_*) → clé GOOD (convention d'affichage Irminsul).
SPECIALIZED_TO_GOOD: dict[str, str] = {
    "FIGHT_PROP_HP_PERCENT": "hp_",
    "FIGHT_PROP_ATTACK_PERCENT": "atk_",
    "FIGHT_PROP_DEFENSE_PERCENT": "def_",
    "FIGHT_PROP_CRITICAL": "critRate_",
    "FIGHT_PROP_CRITICAL_HURT": "critDMG_",
    "FIGHT_PROP_CHARGE_EFFICIENCY": "enerRech_",
    "FIGHT_PROP_ELEMENT_MASTERY": "eleMas",
    "FIGHT_PROP_HEAL_ADD": "heal_",
    "FIGHT_PROP_PHYSICAL_ADD_HURT": "physical_dmg_",
    "FIGHT_PROP_FIRE_ADD_HURT": "pyro_dmg_",
    "FIGHT_PROP_WATER_ADD_HURT": "hydro_dmg_",
    "FIGHT_PROP_ELEC_ADD_HURT": "electro_dmg_",
    "FIGHT_PROP_ICE_ADD_HURT": "cryo_dmg_",
    "FIGHT_PROP_WIND_ADD_HURT": "anemo_dmg_",
    "FIGHT_PROP_ROCK_ADD_HURT": "geo_dmg_",
    "FIGHT_PROP_GRASS_ADD_HURT": "dendro_dmg_",
}

# Seule la Maîtrise élémentaire est une valeur BRUTE ; toutes les autres stats
# d'ascension sont des pourcentages stockés en décimal (×100 pour la convention GOOD).
RAW_VALUE_STATS = {"eleMas"}

# Sources de la FORMULE (mécanique stable, indépendante du patch live).
FORMULA_SOURCES = [
    {"name": "KQM — Character Stats / Scaling", "type": "B",
     "url": "https://library.keqingmains.com/combat-mechanics/character/stats"},
    {"name": "genshin-db (theBowja) — game data", "type": "B",
     "url": "https://github.com/theBowja/genshin-db"},
]


class UnsupportedCharacterError(ValueError):
    """Personnage absent de la source locale → non pris en charge (jamais inventé)."""


def normalize_key(good_key: str) -> str:
    """Clé GOOD (ex. ``KamisatoAyaka``, ``TravelerElectro``) → clé genshin-db.

    Règle : minuscule + suppression des non-alphanumériques. Cas spécial Voyageur :
    ``Aether``/``Lumine``/``Traveler`` et ``Traveler<Élément connu>`` → ``aether``
    (stats identiques, vérifié). Une variante INCONNUE (ex. ``TravelerXyz``) n'est PAS
    rattachée à aether : elle reste telle quelle et sera signalée non prise en charge.
    """
    norm = re.sub(r"[^a-z0-9]", "", str(good_key).lower())
    if norm in {"aether", "lumine", "traveler", "traveller"}:
        return "aether"
    if norm.startswith("traveler"):
        suffix = norm[len("traveler"):]
        if suffix in _TRAVELER_ELEMENTS:
            return "aether"
    return norm


def specialized_to_good(fightprop: str) -> str | None:
    return SPECIALIZED_TO_GOOD.get(fightprop)


def convert_specialized_value(good_key: str, raw: float) -> float:
    """Valeur de stat d'ascension genshin-db → convention d'affichage GOOD.

    EM = brute ; tout le reste = pourcentage décimal → ×100 (ex. 0.384 → 38.4)."""
    if good_key in RAW_VALUE_STATS:
        return float(raw)
    return float(raw) * 100.0


_REL = Path("data") / "mechanics" / "character-basestats.json"


def _candidate_roots() -> list[Path]:
    """Racines où chercher la donnée EMBARQUÉE (voyage avec le moteur, pas avec les
    données utilisateur). Donc indépendante de IRMINSUL_PROJECT_ROOT (réservé au compte).
    Ordre : sidecar gelé → dépôt relatif au paquet → project_root (filet de sécurité)."""
    roots: list[Path] = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        roots.append(Path(sys._MEIPASS))  # type: ignore[attr-defined]
    # src/irminsul/basestats.py → parents[2] = racine du dépôt en dev/tests.
    roots.append(Path(__file__).resolve().parents[2])
    roots.append(project_root())
    return roots


def data_path() -> Path:
    """Premier emplacement existant de la donnée committée ; sinon le candidat
    paquet (pour un message d'erreur clair)."""
    for root in _candidate_roots():
        candidate = root / _REL
        if candidate.exists():
            return candidate
    return _candidate_roots()[0] / _REL


@lru_cache(maxsize=1)
def _load_cached(path_str: str, mtime: float) -> dict[str, Any]:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def load_basestats() -> dict[str, Any]:
    """Charge le JSON committé (caché sur (chemin, mtime) → relecture si régénéré)."""
    p = data_path()
    if not p.exists():
        raise FileNotFoundError(
            f"Données de stats de base absentes : {p}. "
            "Régénérer via `python tools/extract_basestats.py`."
        )
    return _load_cached(str(p), p.stat().st_mtime)


def supported_characters() -> set[str]:
    """Ensemble des clés genshin-db disponibles (clés normalisées)."""
    return set(load_basestats().get("characters", {}).keys())


@dataclass(slots=True)
class CharacterBaseStats:
    key: str            # clé GOOD telle que fournie
    resolved_key: str   # clé genshin-db résolue
    level: int
    ascension: int
    hp: float
    atk: float
    defense: float
    crit_rate_: float   # base, en % (généralement 5.0)
    crit_dmg_: float    # base, en % (généralement 50.0)
    ascension_stat_key: str
    ascension_stat_value: float
    curves: dict[str, str]
    provenance: dict[str, Any]
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # "defense" → "def" pour la sortie (cohérence avec le reste de l'app).
        d["def"] = d.pop("defense")
        return d


def _curve_value(data: dict[str, Any], curve_name: str, level: int) -> float:
    curve = data["curves"].get(curve_name)
    if curve is None:
        raise KeyError(f"courbe inconnue: {curve_name}")
    v = curve.get(str(level))
    if v is None:
        raise KeyError(f"niveau {level} absent de la courbe {curve_name}")
    return float(v)


def character_base_stats(key: str, level: int, ascension: int) -> CharacterBaseStats:
    """Stats de base exactes d'un personnage. Lève une erreur **explicite** si le
    personnage est absent de la source ou si (niveau, ascension) sont hors bornes."""
    level = int(level)
    ascension = int(ascension)
    if not (MIN_LEVEL <= level <= MAX_LEVEL):
        raise ValueError(f"niveau hors bornes (1..90): {level}")
    if not (0 <= ascension <= MAX_ASCENSION):
        raise ValueError(f"ascension hors bornes (0..6): {ascension}")
    # Rejet des paires (niveau, ascension) IMPOSSIBLES en jeu (ex. niv 90 à l'asc 0) :
    # on ne calcule pas une valeur fausse sur des données incohérentes.
    lo, hi = ASCENSION_LEVEL_FLOOR[ascension], ASCENSION_LEVEL_CAP[ascension]
    if not (lo <= level <= hi):
        raise ValueError(
            f"paire niveau/ascension impossible: niveau {level} à l'ascension "
            f"{ascension} (plage attendue {lo}..{hi})"
        )

    data = load_basestats()
    rk = normalize_key(key)
    char = data.get("characters", {}).get(rk)
    if char is None:
        raise UnsupportedCharacterError(
            f"personnage non pris en charge: {key!r} (clé résolue {rk!r} absente de "
            f"genshin-db {data.get('provenance', {}).get('source_commit', '?')[:8]})"
        )

    base = char["base"]
    hp = base["hp"] * _curve_value(data, char["curve"]["hp"], level) \
        + char["promotion"][ascension]["hp"]
    atk = base["atk"] * _curve_value(data, char["curve"]["atk"], level) \
        + char["promotion"][ascension]["atk"]
    df = base["def"] * _curve_value(data, char["curve"]["def"], level) \
        + char["promotion"][ascension]["def"]

    asc_key = char["ascension_stat"]
    asc_val = float(char["promotion"][ascension]["ascension"])

    # Garde-fou : aucune stat de base ne doit être NaN/infinie (donnée corrompue).
    for label, value in (("PV", hp), ("ATQ", atk), ("DÉF", df), ("ascension", asc_val)):
        if not math.isfinite(value):
            raise ValueError(f"valeur de base non finie ({label}) pour {key!r} — données corrompues")

    prov = dict(data.get("provenance", {}))
    prov["formula"] = data.get("provenance", {}).get(
        "formula", "stat = base × courbe[niveau] + promotion[ascension]")
    return CharacterBaseStats(
        key=str(key),
        resolved_key=rk,
        level=level,
        ascension=ascension,
        hp=round(hp, 2),
        atk=round(atk, 2),
        defense=round(df, 2),
        crit_rate_=round(float(char.get("base_crit_rate_", 5.0)), 2),
        crit_dmg_=round(float(char.get("base_crit_dmg_", 50.0)), 2),
        ascension_stat_key=asc_key,
        ascension_stat_value=round(asc_val, 4),
        curves=dict(char["curve"]),
        provenance=prov,
        confidence=str(data.get("provenance", {}).get("confidence", "high")),
    )


def character_base_stats_payload(key: str, level: int, ascension: int) -> dict[str, Any]:
    """Variante structurée pour l'IPC : ``{"supported": True, ...}`` ou, si absent,
    ``{"supported": False, "reason": ...}`` — sans jamais lever ni inventer."""
    try:
        cbs = character_base_stats(key, level, ascension)
    except UnsupportedCharacterError as exc:
        return {"supported": False, "reason": str(exc), "key": str(key),
                "resolved_key": normalize_key(key)}
    except (ValueError, KeyError, FileNotFoundError) as exc:
        return {"supported": False, "reason": str(exc), "key": str(key)}
    return {"supported": True, **cbs.to_dict()}


# --------------------------------------------------------------------------- #
# Extraction (utilisée par tools/extract_basestats.py ; pure, sans git).
# --------------------------------------------------------------------------- #
def extract_from_genshin_db(source_root: Path, provenance: dict[str, Any]) -> dict[str, Any]:
    """Construit le dict committable depuis un checkout genshin-db.

    `source_root` = .../data/sources/genshin-db. `provenance` est complétée par
    l'appelant (commit, date, etc.). Aucune valeur inventée : on copie/convertit
    fidèlement, et on documente la conversion d'unités de la stat d'ascension.
    """
    sd = source_root / "src" / "data"
    curve_raw = json.loads((sd / "curve" / "characters.json").read_text(encoding="utf-8"))
    stats_raw = json.loads((sd / "stats" / "characters.json").read_text(encoding="utf-8"))

    # Courbes : ne garder que les colonnes réellement utilisées, niveaux 1..90.
    used_curves: set[str] = set()
    for c in stats_raw.values():
        used_curves.update(c["curve"].values())
    curves: dict[str, dict[str, float]] = {}
    for name in sorted(used_curves):
        curves[name] = {
            str(lvl): float(curve_raw[str(lvl)][name])
            for lvl in range(MIN_LEVEL, MAX_LEVEL + 1)
        }

    characters: dict[str, Any] = {}
    for ckey, c in stats_raw.items():
        spec_fp = c.get("specialized")
        good_asc = specialized_to_good(spec_fp) if spec_fp else None
        if good_asc is None:
            # Inconnu : on n'invente pas — on signale en sortie (skip + note).
            raise ValueError(f"stat d'ascension non mappée pour {ckey}: {spec_fp!r}")
        promotion = []
        for ph in c["promotion"]:
            promotion.append({
                "phase": int(ph.get("maxlevel", 0)),
                "hp": float(ph.get("hp", 0.0)),
                "atk": float(ph.get("attack", 0.0)),
                "def": float(ph.get("defense", 0.0)),
                "ascension": convert_specialized_value(good_asc, ph.get("specialized", 0.0)),
            })
        characters[ckey] = {
            "base": {
                "hp": float(c["base"]["hp"]),
                "atk": float(c["base"]["attack"]),
                "def": float(c["base"]["defense"]),
            },
            "base_crit_rate_": round(float(c["base"].get("critrate", 0.05)) * 100.0, 2),
            "base_crit_dmg_": round(float(c["base"].get("critdmg", 0.5)) * 100.0, 2),
            "curve": {
                "hp": c["curve"]["hp"],
                "atk": c["curve"]["attack"],
                "def": c["curve"]["defense"],
            },
            "ascension_stat": good_asc,
            "ascension_stat_fightprop": spec_fp,
            "promotion": promotion,
        }

    prov = dict(provenance)
    prov.setdefault("formula", "stat(niveau, ascension) = base × courbe[niveau] + promotion[ascension]")
    prov.setdefault("formula_sources", FORMULA_SOURCES)
    prov.setdefault("confidence", "high")
    prov["character_count"] = len(characters)
    prov["ascension_value_units"] = (
        "valeurs converties en unités d'affichage : pourcentages ×100, Maîtrise brute"
    )
    return {
        "schema": 1,
        "kind": "character-base-stats",
        "version": prov.get("source_commit_date", prov.get("extracted_at", "")),
        "provenance": prov,
        "curves": curves,
        "characters": dict(sorted(characters.items())),
    }
