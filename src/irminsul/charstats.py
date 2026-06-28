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

from . import basestats
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


# Ce qui n'est volontairement PAS (encore) pris en charge (signalé, jamais présenté
# comme actif). NB : les stats de BASE du personnage sont désormais calculées
# automatiquement (cf. basestats) ; il reste l'arme, les conditionnels et les talents.
UNSUPPORTED = [
    {"item": "stat principale (ATQ de base) & passif d'arme",
     "reason": "base d'arme non encore calculée (tâche suivante) ; passif conditionnel non implémenté → "
               "les stats finales restent INCOMPLÈTES tant que l'arme n'est pas branchée"},
    {"item": "effets conditionnels de set (4p), constellation, talents passifs",
     "reason": "non implémentés — ne pas présenter comme actifs"},
    {"item": "multiplicateur de talent automatique",
     "reason": "à saisir manuellement (scaling) tant que la table de talents n'est pas branchée"},
]

# Marqueur unique : tout ce qui manque encore pour des stats finales COMPLÈTES.
_WEAPON_PENDING = ("arme non incluse (ATQ de base + stat secondaire) — tâche suivante : "
                   "les stats finales ci-dessous sont partielles, hors arme")


def compute_final_stats(base: dict[str, Any], art_totals: dict[str, float]) -> dict[str, Any]:
    """Combine stats de BASE perso (exactes) + artéfacts + stat d'ascension, en
    marquant chaque stat comme INCOMPLÈTE tant que l'arme n'est pas branchée.
    On n'invente rien : la part manquante (arme) est explicitement listée."""
    t: dict[str, float] = {k: float(v) for k, v in art_totals.items()}
    ak = base["ascension_stat_key"]
    t[ak] = round(t.get(ak, 0.0) + float(base["ascension_stat_value"]), 2)

    hp_pct, atk_pct, def_pct = t.get("hp_", 0.0), t.get("atk_", 0.0), t.get("def_", 0.0)
    final_hp = base["hp"] * (1 + hp_pct / 100) + t.get("hp", 0.0)
    final_atk = base["atk"] * (1 + atk_pct / 100) + t.get("atk", 0.0)
    final_def = base["def"] * (1 + def_pct / 100) + t.get("def", 0.0)
    crit_rate = base["crit_rate_"] + t.get("critRate_", 0.0)
    crit_dmg = base["crit_dmg_"] + t.get("critDMG_", 0.0)
    em = t.get("eleMas", 0.0)
    ener = 100.0 + t.get("enerRech_", 0.0)

    def cell(value: float, missing: list[str]) -> dict[str, Any]:
        return {"value": round(value, 2), "complete": False, "missing": missing}

    dmg_bonus = {k: round(v, 2) for k, v in t.items()
                 if k.endswith("_dmg_") or k == "heal_"}

    return {
        "complete": False,
        "note": _WEAPON_PENDING,
        "ascension_stat_applied": {"key": ak, "value": base["ascension_stat_value"]},
        "hp": cell(final_hp, ["stat secondaire d'arme si PV%"]),
        "atk": cell(final_atk, ["ATQ de base de l'arme", "stat secondaire d'arme si ATQ%"]),
        "def": cell(final_def, ["stat secondaire d'arme si DÉF%"]),
        "crit_rate_": cell(crit_rate, ["stat secondaire d'arme si Taux Crit"]),
        "crit_dmg_": cell(crit_dmg, ["stat secondaire d'arme si Dégâts Crit"]),
        "eleMas": cell(em, ["stat secondaire d'arme si Maîtrise"]),
        "enerRech_": cell(ener, ["stat secondaire d'arme si Recharge"]),
        "dmg_bonus": dmg_bonus,
    }


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

    # Stats de BASE live, versionnées et sourcées (genshin-db) — calculées automatiquement.
    base_stats = basestats.character_base_stats_payload(
        key, c.get("level") or 1, c.get("ascension") or 0)
    final_stats: dict[str, Any] | None = None
    unsupported = list(UNSUPPORTED)
    if base_stats.get("supported"):
        final_stats = compute_final_stats(base_stats, art_stats["totals"])
    else:
        unsupported.append({
            "item": "stats de base du personnage (PV/ATQ/DÉF)",
            "reason": base_stats.get("reason", "personnage absent de la source locale")
                      + " → saisir l'ATQ/PV finale du jeu",
        })

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
            "base_stats": base_stats,
            "final_stats": final_stats,
            "unsupported": unsupported,
            "provenance": _provenance(cur),
        },
    }
