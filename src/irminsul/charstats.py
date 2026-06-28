"""Statistiques de personnage à partir du compte GOOD importé.

Principe d'honnêteté : on calcule **exactement** ce qui est dérivable du GOOD
(artéfacts : substats réels + table FIXE des stats principales 5★ niv.20), et on
**signale comme non pris en charge** ce qui nécessite des données absentes de la
source locale (stats de BASE perso/arme = courbes non fournies par genshin-db),
ainsi que les effets conditionnels d'arme/set/constellation. On n'invente rien.
"""

from __future__ import annotations

import math
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
    anomalies: list[dict[str, Any]] = []
    for a in artifacts:
        for s in a.get("substats") or []:
            key = s.get("key")
            if not key:
                continue
            try:
                val = float(s.get("value", 0) or 0)
            except (TypeError, ValueError):
                anomalies.append({"set": a.get("setKey"), "slot": a.get("slotKey"),
                                  "key": key, "value": s.get("value"),
                                  "reason": "substat non numérique (ignorée, jamais inventée)"})
                continue
            if not math.isfinite(val):
                anomalies.append({"set": a.get("setKey"), "slot": a.get("slotKey"),
                                  "key": key, "value": s.get("value"),
                                  "reason": "substat NaN/infinie (ignorée — donnée corrompue)"})
                continue
            totals[key] += val
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
            "uncomputed_main": uncomputed, "anomalies": anomalies}


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

# Stat principale d'artéfact (clé GOOD) → cellule de stat finale impactée.
_MAIN_TO_CELL = {
    "hp": "hp", "hp_": "hp", "atk": "atk", "atk_": "atk", "def": "def", "def_": "def",
    "critRate_": "crit_rate_", "critDMG_": "crit_dmg_", "eleMas": "eleMas", "enerRech_": "enerRech_",
}


def compute_final_stats(
    base: dict[str, Any],
    art_totals: dict[str, float],
    uncomputed_main: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Combine stats de BASE perso (exactes) + artéfacts + stat d'ascension, en
    marquant chaque stat comme INCOMPLÈTE tant que l'arme n'est pas branchée ET en
    signalant toute stat principale d'artéfact non calculée (honnêteté : la part
    manquante — arme ou main d'artéfact — est explicitement listée, jamais inventée)."""
    t: dict[str, float] = {}
    for k, v in art_totals.items():
        fv = float(v)
        if math.isfinite(fv):  # garde anti NaN/inf (corruption en amont)
            t[k] = fv
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

    # C4 : répercuter les stats PRINCIPALES d'artéfact non calculées sur les bonnes cellules.
    extra_missing: dict[str, list[str]] = defaultdict(list)
    main_incomplete: list[str] = []
    for u in uncomputed_main or []:
        mk = u.get("mainStatKey")
        main_incomplete.append(str(mk))
        cell_key = _MAIN_TO_CELL.get(mk)
        if cell_key:
            extra_missing[cell_key].append(
                f"stat principale d'artéfact non calculée ({mk}, {u.get('rarity')}★ niv{u.get('level')})"
            )

    def cell(name: str, value: float, missing: list[str]) -> dict[str, Any]:
        full = list(missing) + extra_missing.get(name, [])
        out = round(value, 2)
        if not math.isfinite(out):  # ne jamais émettre NaN/inf
            return {"value": None, "complete": False, "missing": full + ["valeur non finie rejetée"]}
        return {"value": out, "complete": False, "missing": full}

    dmg_bonus = {k: round(v, 2) for k, v in t.items()
                 if k.endswith("_dmg_") or k == "heal_"}

    return {
        "complete": False,
        "note": _WEAPON_PENDING,
        "ascension_stat_applied": {"key": ak, "value": base["ascension_stat_value"]},
        "artifact_main_incomplete": main_incomplete,
        "hp": cell("hp", final_hp, ["stat secondaire d'arme si PV%"]),
        "atk": cell("atk", final_atk, ["ATQ de base de l'arme", "stat secondaire d'arme si ATQ%"]),
        "def": cell("def", final_def, ["stat secondaire d'arme si DÉF%"]),
        "crit_rate_": cell("crit_rate_", crit_rate, ["stat secondaire d'arme si Taux Crit"]),
        "crit_dmg_": cell("crit_dmg_", crit_dmg, ["stat secondaire d'arme si Dégâts Crit"]),
        "eleMas": cell("eleMas", em, ["stat secondaire d'arme si Maîtrise"]),
        "enerRech_": cell("enerRech_", ener, ["stat secondaire d'arme si Recharge"]),
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
        final_stats = compute_final_stats(
            base_stats, art_stats["totals"], art_stats.get("uncomputed_main"))
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
