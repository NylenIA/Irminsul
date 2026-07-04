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

from . import basestats, talentstats, weaponstats
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


def _level_or(value: Any, default: int = 1) -> int:
    """Niveau du scan : fallback UNIQUEMENT si None/non-entier. Un 0 falsy réel est conservé
    (→ rejeté par les gardes de basestats/weaponstats, jamais promu en niveau 1 « plausible »)."""
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _ascension_or(value: Any, default: int = 0) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else default


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
            raw_val = s.get("value")
            # Audit Codex : une value absente/None n'est PAS un 0 silencieux → anomalie explicite.
            if raw_val is None:
                anomalies.append({"set": a.get("setKey"), "slot": a.get("slotKey"),
                                  "key": key, "value": None,
                                  "reason": "substat sans valeur (ignorée, jamais inventée)"})
                continue
            try:
                val = float(raw_val)
            except (TypeError, ValueError):
                # value sérialisée en str → JSON toujours valide (jamais de NaN brut en sortie).
                anomalies.append({"set": a.get("setKey"), "slot": a.get("slotKey"),
                                  "key": key, "value": str(raw_val),
                                  "reason": "substat non numérique (ignorée, jamais inventée)"})
                continue
            if not math.isfinite(val):
                anomalies.append({"set": a.get("setKey"), "slot": a.get("slotKey"),
                                  "key": key, "value": str(raw_val),
                                  "reason": "substat NaN/infinie (ignorée — donnée corrompue)"})
                continue
            totals[key] += val
        mk = a.get("mainStatKey")
        if not mk:
            # Audit Codex : artéfact sans stat principale → anomalie (pas un abandon silencieux).
            anomalies.append({"set": a.get("setKey"), "slot": a.get("slotKey"),
                              "reason": "artéfact sans stat principale (ignoré — donnée incomplète)"})
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
# comme actif). NB : les stats de BASE perso ET arme sont calculées (cf. basestats /
# weaponstats) ; il reste les passifs/effets CONDITIONNELS et les multiplicateurs de talent.
UNSUPPORTED = [
    {"item": "passif d'arme & effets conditionnels (set 4p, constellation, talents passifs)",
     "reason": "non implémentés (situationnels) — hors stats de base ; ne pas présenter comme actifs. "
               "Les stats finales correspondent à l'écran du personnage en jeu (hors buffs conditionnels)."},
    {"item": "passifs de talent (1er/4e) & buffs conditionnels de talent",
     "reason": "les MULTIPLICATEURS de talent sont fournis (cf. talents_detail, libellés du jeu) ; "
               "les passifs/buffs conditionnels ne sont pas appliqués automatiquement"},
]

# Stat principale d'artéfact (clé GOOD) → cellule de stat finale impactée.
_MAIN_TO_CELL = {
    "hp": "hp", "hp_": "hp", "atk": "atk", "atk_": "atk", "def": "def", "def_": "def",
    "critRate_": "crit_rate_", "critDMG_": "crit_dmg_", "eleMas": "eleMas", "enerRech_": "enerRech_",
}

_COMPLETE_NOTE = ("stats finales = écran du personnage en jeu (base perso + arme + artéfacts) ; "
                  "hors buffs CONDITIONNELS (passifs d'arme/set/constellation), appliqués au calcul, pas à la fiche")


def compute_final_stats(
    base: dict[str, Any],
    art_totals: dict[str, float],
    uncomputed_main: list[dict[str, Any]] | None = None,
    weapon: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine base perso (exacte) + ARME (ATQ de base + stat secondaire) + artéfacts +
    stat d'ascension. Une stat est `complete` quand l'arme est prise en charge ET qu'aucune
    stat principale d'artéfact ne manque → elle correspond alors à l'écran du jeu (hors buffs
    conditionnels). Tout ce qui manque est listé ; rien n'est inventé."""
    t: dict[str, float] = {}
    for k, v in art_totals.items():
        fv = float(v)
        if math.isfinite(fv):  # garde anti NaN/inf (corruption en amont)
            t[k] = fv
    ak = base["ascension_stat_key"]
    t[ak] = round(t.get(ak, 0.0) + float(base["ascension_stat_value"]), 2)

    # --- Contribution de l'ARME (ATQ de base + stat secondaire) --- #
    # R3/#4 : NE JAMAIS faire confiance aveuglément au payload. 'supported' ne suffit pas :
    # on EXIGE une ATQ de base finie (et une secondaire finie si une clé secondaire existe).
    # Sinon → dégradation explicite (pas de 0 silencieux, pas de complete=true mensonger).
    weapon = weapon or {}
    weapon_supported = bool(weapon.get("supported"))

    def _num(x: Any) -> float | None:
        try:
            f = float(x)
        except (TypeError, ValueError):
            return None
        return f if math.isfinite(f) else None

    weapon_atk_val = _num(weapon.get("base_atk")) if weapon_supported else None
    sec_key = weapon.get("secondary_stat_key") if weapon_supported else None
    sec_val = _num(weapon.get("secondary_stat_value")) if weapon_supported else None
    # Arme « valide » = prise en charge ET ATQ de base finie ET (pas de secondaire OU secondaire finie).
    weapon_valid = weapon_supported and weapon_atk_val is not None and (sec_key is None or sec_val is not None)
    weapon_atk = weapon_atk_val if weapon_valid else 0.0
    if weapon_valid and sec_key and sec_val is not None:
        t[sec_key] = round(t.get(sec_key, 0.0) + sec_val, 2)

    hp_pct, atk_pct, def_pct = t.get("hp_", 0.0), t.get("atk_", 0.0), t.get("def_", 0.0)
    final_hp = base["hp"] * (1 + hp_pct / 100) + t.get("hp", 0.0)
    # ATQ% s'applique à (ATQ base perso + ATQ base ARME) ; ATQ plate des artéfacts ajoutée après.
    final_atk = (base["atk"] + weapon_atk) * (1 + atk_pct / 100) + t.get("atk", 0.0)
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

    # Arme non valide (absente, non prise en charge, ou métadonnées invalides) : sa stat
    # secondaire est INCONNUE et l'ATQ manque sa base → marquer incomplet partout (jamais
    # de complete=true mensonger, jamais de 0 silencieux présenté comme réel).
    weapon_missing: list[str] = []
    if not weapon_valid:
        if weapon_supported:
            weapon_missing.append(
                "métadonnées d'arme invalides (ATQ de base absente/non finie) — non incluses")
        else:
            weapon_missing.append(
                weapon.get("reason") or "arme non prise en charge (ATQ de base + stat secondaire inconnus)")

    def cell(name: str, value: float) -> dict[str, Any]:
        miss = list(weapon_missing) + extra_missing.get(name, [])
        complete = weapon_valid and not extra_missing.get(name)
        out = round(value, 2)
        if not math.isfinite(out):  # ne jamais émettre NaN/inf
            return {"value": None, "complete": False, "missing": miss + ["valeur non finie rejetée"]}
        return {"value": out, "complete": complete, "missing": miss}

    dmg_bonus = {k: round(v, 2) for k, v in t.items()
                 if k.endswith("_dmg_") or k == "heal_"}

    all_complete = weapon_valid and not main_incomplete
    return {
        "complete": all_complete,
        "note": _COMPLETE_NOTE if all_complete else
                "stats finales PARTIELLES : " + "; ".join(weapon_missing + (
                    ["stat principale d'artéfact non calculée"] if main_incomplete else [])),
        "weapon": {"supported": weapon_supported, "valid": weapon_valid, "key": weapon.get("key"),
                   "base_atk": round(weapon_atk_val, 2) if weapon_atk_val is not None else None,
                   "secondary_stat_key": sec_key,
                   "secondary_stat_value": round(sec_val, 4) if sec_val is not None else None},
        "ascension_stat_applied": {"key": ak, "value": base["ascension_stat_value"]},
        "artifact_main_incomplete": main_incomplete,
        "hp": cell("hp", final_hp),
        "atk": cell("atk", final_atk),
        "def": cell("def", final_def),
        "crit_rate_": cell("crit_rate_", crit_rate),
        "crit_dmg_": cell("crit_dmg_", crit_dmg),
        "eleMas": cell("eleMas", em),
        "enerRech_": cell("enerRech_", ener),
        "dmg_bonus": dmg_bonus,
    }


def character_talents_detail(key: str, talents: dict[str, Any]) -> dict[str, Any]:
    """Attributs de talents étiquetés AU NIVEAU RÉEL du perso (auto/skill/burst →
    combat1/2/3). Permet de remplacer la saisie manuelle du `scaling` par un choix
    sourcé (libellé exact du jeu). Non pris en charge → signalé, jamais inventé."""
    mapping = {"normal": talents.get("auto"), "skill": talents.get("skill"),
               "burst": talents.get("burst")}
    out: dict[str, Any] = {}
    for slot, lvl in mapping.items():
        if lvl:
            out[slot] = talentstats.talent_attributes(key, slot, int(lvl))
        else:
            out[slot] = {"supported": False, "reason": "niveau de talent inconnu (GOOD incomplet)"}
    out["any_supported"] = any(v.get("supported") for v in out.values() if isinstance(v, dict))
    return out


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
    # Audit Codex : fallback UNIQUEMENT pour None (absent). Un niveau falsy réel (0) est passé
    # tel quel → rejeté par les gardes de basestats (jamais promu en niveau 1 « plausible »).
    base_stats = basestats.character_base_stats_payload(
        key, _level_or(c.get("level")), _ascension_or(c.get("ascension")))
    # Stats de BASE d'arme (genshin-db) — calculées automatiquement, sourcées, versionnées.
    if w:
        weapon_bs = weaponstats.weapon_base_stats_payload(
            w["key"], _level_or(w.get("level")), _ascension_or(w.get("ascension")))
        weapon_bs.setdefault("key", w["key"])
    else:
        weapon_bs = {"supported": False, "reason": "aucune arme équipée", "key": None}

    final_stats: dict[str, Any] | None = None
    unsupported = list(UNSUPPORTED)
    if base_stats.get("supported"):
        final_stats = compute_final_stats(
            base_stats, art_stats["totals"], art_stats.get("uncomputed_main"), weapon_bs)
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
            "weapon_base_stats": weapon_bs,
            "final_stats": final_stats,
            "talents_detail": character_talents_detail(key, c.get("talents") or {}),
            "unsupported": unsupported,
            "provenance": _provenance(cur),
        },
    }
