"""Statistiques de personnage à partir du compte GOOD importé.

Principe d'honnêteté : on calcule **exactement** ce qui est dérivable du GOOD
(artéfacts : substats réels + table FIXE des stats principales 5★ niv.20), et on
**signale comme non pris en charge** ce qui nécessite des données absentes de la
source locale (stats de BASE perso/arme = courbes non fournies par genshin-db),
ainsi que les effets conditionnels d'arme/set/constellation. On n'invente rien.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .account import load_current

# Valeurs EXACTES des stats principales d'artéfact 5★ au niveau 20 (publiques,
# vérifiables en jeu / KQM / Genshin Optimizer). Clés au format GOOD.
MAIN_STAT_5STAR_L20: dict[str, float] = {
    "hp": 4780.0,
    "atk": 311.0,
    "hp_": 46.6,
    "atk_": 46.6,
    "def_": 58.3,
    "eleMas": 187.0,
    "enerRech_": 51.8,
    "critRate_": 31.1,
    "critDMG_": 62.2,
    "heal_": 35.9,
    "physical_dmg_": 58.3,
    "pyro_dmg_": 46.6,
    "hydro_dmg_": 46.6,
    "electro_dmg_": 46.6,
    "cryo_dmg_": 46.6,
    "anemo_dmg_": 46.6,
    "geo_dmg_": 46.6,
    "dendro_dmg_": 46.6,
}


def artifact_stat_totals(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Somme exacte des stats issues des artéfacts : substats (valeurs réelles du
    GOOD) + stats principales (table 5★ niv.20). Les pièces hors de cette table
    sont listées comme non calculées (jamais approximées)."""
    totals: dict[str, float] = defaultdict(float)
    uncomputed: list[dict[str, Any]] = []
    for a in artifacts:
        for s in a.get("substats") or []:
            key = s.get("key")
            if key:
                totals[key] += float(s.get("value", 0) or 0)
        mk = a.get("mainStatKey")
        if not mk:
            continue
        if a.get("rarity") == 5 and a.get("level") == 20 and mk in MAIN_STAT_5STAR_L20:
            totals[mk] += MAIN_STAT_5STAR_L20[mk]
        else:
            uncomputed.append({
                "set": a.get("setKey"), "slot": a.get("slotKey"),
                "rarity": a.get("rarity"), "level": a.get("level"), "mainStatKey": mk,
                "reason": "stat principale non calculée (table limitée au 5★ niveau 20)",
            })
    return {"totals": {k: round(v, 2) for k, v in totals.items()},
            "uncomputed_main": uncomputed}


def _provenance(cur: dict[str, Any]) -> dict[str, Any]:
    p = cur["account-profile"]
    return {"snapshot_date": p.get("snapshot_date"), "source": p.get("source"),
            "sha256": p.get("sha256"), "good_version": p.get("good_version")}


def characters_payload() -> dict[str, Any]:
    try:
        cur = load_current()
    except FileNotFoundError:
        return {"status": "empty"}
    return {"status": "ok", "characters": sorted(cur["characters"]["characters"].keys())}


# Ce qui n'est volontairement PAS pris en charge (signalé, jamais présenté comme actif).
UNSUPPORTED = [
    {"item": "stats de base du personnage (PV/ATQ/DÉF de base)",
     "reason": "courbes de base absentes de la source locale (genshin-db) → saisir l'ATQ/PV finale du jeu"},
    {"item": "stat principale & passif d'arme",
     "reason": "base d'arme non calculée ; passif conditionnel non implémenté"},
    {"item": "effets conditionnels de set (4p), constellation, talents passifs",
     "reason": "non implémentés — ne pas présenter comme actifs"},
    {"item": "multiplicateur de talent automatique",
     "reason": "à saisir manuellement (scaling) tant que la table de talents n'est pas branchée"},
]


def character_payload(key: str) -> dict[str, Any]:
    try:
        cur = load_current()
    except FileNotFoundError:
        return {"status": "empty"}
    chars = cur["characters"]["characters"]
    if key not in chars:
        return {"status": "not_found", "key": key}
    c = chars[key]
    weapons = cur["weapons"]["weapons"]
    arts = cur["artifacts"]["artifacts"]
    wid = c.get("weapon")
    w = weapons.get(wid) if wid else None
    equipped = [arts[a] for a in (c.get("artifacts") or {}).values() if a in arts]
    art_stats = artifact_stat_totals(equipped)
    return {
        "status": "ok",
        "character": {
            "key": key,
            "level": c.get("level"),
            "ascension": c.get("ascension"),
            "constellation": c.get("constellation"),
            "talents": c.get("talents") or {},
            "weapon": ({"key": w["key"], "level": w["level"], "refinement": w["refinement"]}
                       if w else None),
            "artifacts": [{"setKey": a["setKey"], "slotKey": a["slotKey"], "rarity": a["rarity"],
                           "level": a["level"], "mainStatKey": a["mainStatKey"]} for a in equipped],
            "artifact_stats": art_stats,
            "unsupported": UNSUPPORTED,
            "provenance": _provenance(cur),
        },
    }
