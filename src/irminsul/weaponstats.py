"""Statistiques de BASE des armes (ATQ de base + stat secondaire, par niveau+ascension).

Même patron éprouvé que `basestats` (personnages) :
    ATQ(niveau, ascension) = base_atk × courbe_atk[niveau] + promotion[ascension]
    secondaire(niveau)     = base_secondary × courbe_secondary[niveau]   (sans ascension)

Données extraites de genshin-db (gitignoré) vers le fichier **committé**
`data/mechanics/weapon-basestats.json` (provenance reproductible : commit + date du
commit + formule + confiance), embarqué dans le sidecar. On ne calcule QUE les armes
présentes dans la source ; tout le reste est signalé non pris en charge (jamais inventé).
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

from .basestats import (
    ASCENSION_LEVEL_CAP,
    ASCENSION_LEVEL_FLOOR,
    MAX_LEVEL,
    MIN_LEVEL,
    SPECIALIZED_TO_GOOD,
    convert_specialized_value,
)
from .paths import project_root

# Stat secondaire « aucune » (certaines armes 1★/2★) → pas de secondaire.
_NONE_FIGHTPROP = "FIGHT_PROP_NONE"

FORMULA_SOURCES = [
    {"name": "KQM — Weapon Stats / Scaling", "type": "B",
     "url": "https://library.keqingmains.com/combat-mechanics/character/stats"},
    {"name": "genshin-db (theBowja) — game data", "type": "B",
     "url": "https://github.com/theBowja/genshin-db"},
]


class UnsupportedWeaponError(ValueError):
    """Arme absente de la source locale → non prise en charge (jamais inventée)."""


def normalize_key(good_key: str) -> str:
    """Clé GOOD d'arme (ex. ``MistsplitterReforged``) → clé genshin-db (minuscule, alphanum)."""
    return re.sub(r"[^a-z0-9]", "", str(good_key).lower())


_REL = Path("data") / "mechanics" / "weapon-basestats.json"


def _candidate_roots() -> list[Path]:
    roots: list[Path] = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        roots.append(Path(sys._MEIPASS))  # type: ignore[attr-defined]
    roots.append(Path(__file__).resolve().parents[2])
    roots.append(project_root())
    return roots


def data_path() -> Path:
    for root in _candidate_roots():
        candidate = root / _REL
        if candidate.exists():
            return candidate
    return _candidate_roots()[0] / _REL


@lru_cache(maxsize=1)
def _load_cached(path_str: str, mtime: float) -> dict[str, Any]:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def load_weaponstats() -> dict[str, Any]:
    p = data_path()
    if not p.exists():
        raise FileNotFoundError(
            f"Données de stats d'arme absentes : {p}. "
            "Régénérer via `python tools/extract_weapon_basestats.py`."
        )
    return _load_cached(str(p), p.stat().st_mtime)


def supported_weapons() -> set[str]:
    return set(load_weaponstats().get("weapons", {}).keys())


@dataclass(slots=True)
class WeaponBaseStats:
    key: str
    resolved_key: str
    level: int
    ascension: int
    base_atk: float
    secondary_stat_key: str | None
    secondary_stat_value: float
    max_level: int
    max_ascension: int
    provenance: dict[str, Any]
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _curve_value(data: dict[str, Any], curve_name: str, level: int) -> float:
    curve = data["curves"].get(curve_name)
    if curve is None:
        raise KeyError(f"courbe d'arme inconnue: {curve_name}")
    v = curve.get(str(level))
    if v is None:
        raise KeyError(f"niveau {level} absent de la courbe {curve_name}")
    return float(v)


def weapon_base_stats(key: str, level: int, ascension: int) -> WeaponBaseStats:
    """ATQ de base + stat secondaire exactes d'une arme. Erreurs EXPLICITES si l'arme
    est absente ou si (niveau, ascension) sont hors bornes pour SA rareté."""
    level = int(level)
    ascension = int(ascension)
    if not (MIN_LEVEL <= level <= MAX_LEVEL):
        raise ValueError(f"niveau hors bornes (1..90): {level}")
    if ascension < 0:
        raise ValueError(f"ascension négative: {ascension}")

    data = load_weaponstats()
    rk = normalize_key(key)
    wp = data.get("weapons", {}).get(rk)
    if wp is None:
        raise UnsupportedWeaponError(
            f"arme non prise en charge: {key!r} (clé résolue {rk!r} absente de genshin-db "
            f"{data.get('provenance', {}).get('source_commit', '?')[:8]})"
        )

    max_asc = int(wp["max_ascension"])
    max_lvl = int(wp["max_level"])
    if ascension > max_asc:
        raise ValueError(f"ascension {ascension} > max {max_asc} pour {key!r} (rareté plus basse)")
    if level > max_lvl:
        raise ValueError(f"niveau {level} > max {max_lvl} pour {key!r} (rareté plus basse)")
    lo = ASCENSION_LEVEL_FLOOR[ascension]
    hi = min(ASCENSION_LEVEL_CAP[ascension], max_lvl)
    if not (lo <= level <= hi):
        raise ValueError(
            f"paire niveau/ascension impossible: niveau {level} à l'ascension {ascension} "
            f"(plage attendue {lo}..{hi}) pour {key!r}"
        )

    base_atk = wp["base_atk"] * _curve_value(data, wp["curve_atk"], level) \
        + wp["promotion"][ascension]["atk"]

    sec_key = wp.get("secondary_stat")
    sec_val = 0.0
    if sec_key:
        raw = wp["base_secondary"] * _curve_value(data, wp["curve_secondary"], level)
        sec_val = convert_specialized_value(sec_key, raw)

    for label, value in (("ATQ", base_atk), ("secondaire", sec_val)):
        if not math.isfinite(value):
            raise ValueError(f"valeur d'arme non finie ({label}) pour {key!r} — données corrompues")

    return WeaponBaseStats(
        key=str(key),
        resolved_key=rk,
        level=level,
        ascension=ascension,
        base_atk=round(base_atk, 2),
        secondary_stat_key=sec_key,
        secondary_stat_value=round(sec_val, 4),
        max_level=max_lvl,
        max_ascension=max_asc,
        provenance=dict(data.get("provenance", {})),
        confidence=str(data.get("provenance", {}).get("confidence", "high")),
    )


def weapon_base_stats_payload(key: str, level: int, ascension: int) -> dict[str, Any]:
    """Variante structurée pour l'IPC : ``{"supported": True, ...}`` ou, si absent,
    ``{"supported": False, "reason": ...}`` — sans jamais lever ni inventer."""
    try:
        wbs = weapon_base_stats(key, level, ascension)
    except UnsupportedWeaponError as exc:
        return {"supported": False, "reason": str(exc), "key": str(key),
                "resolved_key": normalize_key(key)}
    except (ValueError, KeyError, FileNotFoundError) as exc:
        return {"supported": False, "reason": str(exc), "key": str(key)}
    return {"supported": True, **wbs.to_dict()}


# --------------------------------------------------------------------------- #
# Extraction (pure, sans git) — utilisée par tools/extract_weapon_basestats.py.
# --------------------------------------------------------------------------- #
def extract_weapons_from_genshin_db(source_root: Path, provenance: dict[str, Any]) -> dict[str, Any]:
    sd = source_root / "src" / "data"
    curve_raw = json.loads((sd / "curve" / "weapons.json").read_text(encoding="utf-8"))
    stats_raw = json.loads((sd / "stats" / "weapons.json").read_text(encoding="utf-8"))

    used_curves: set[str] = set()
    for w in stats_raw.values():
        used_curves.add(w["curve"]["attack"])
        cs = w["curve"].get("specialized")
        if cs:
            used_curves.add(cs)
    curves: dict[str, dict[str, float]] = {}
    for name in sorted(used_curves):
        curves[name] = {
            str(lvl): float(curve_raw[str(lvl)][name])
            for lvl in range(MIN_LEVEL, MAX_LEVEL + 1)
            if name in curve_raw[str(lvl)]
        }

    weapons: dict[str, Any] = {}
    for wkey, w in stats_raw.items():
        spec_fp = w.get("specialized")
        if spec_fp and spec_fp != _NONE_FIGHTPROP:
            good_sec = SPECIALIZED_TO_GOOD.get(spec_fp)
            if good_sec is None:
                raise ValueError(f"stat secondaire non mappée pour {wkey}: {spec_fp!r}")
        else:
            good_sec = None
        promotion = [{"phase": int(ph.get("maxlevel", 0)), "atk": float(ph.get("attack", 0.0))}
                     for ph in w["promotion"]]
        max_asc = len(promotion) - 1
        max_lvl = int(w["promotion"][-1].get("maxlevel", MAX_LEVEL))
        weapons[wkey] = {
            "base_atk": float(w["base"]["attack"]),
            "base_secondary": float(w["base"].get("specialized", 0.0) or 0.0),
            "curve_atk": w["curve"]["attack"],
            "curve_secondary": w["curve"].get("specialized"),
            "secondary_stat": good_sec,
            "secondary_stat_fightprop": spec_fp,
            "max_level": max_lvl,
            "max_ascension": max_asc,
            "promotion": promotion,
        }

    prov = dict(provenance)
    prov.setdefault("formula",
                    "ATQ = base × courbe_atk[niveau] + promotion[ascension] ; "
                    "secondaire = base_secondary × courbe_secondary[niveau] (sans ascension)")
    prov.setdefault("formula_sources", FORMULA_SOURCES)
    prov["weapon_count"] = len(weapons)
    prov["secondary_value_units"] = "pourcentages ×100, Maîtrise brute (idem perso)"
    return {
        "schema": 1,
        "kind": "weapon-base-stats",
        "version": prov.get("source_commit_date", prov.get("extracted_at", "")),
        "provenance": prov,
        "curves": curves,
        "weapons": dict(sorted(weapons.items())),
    }
