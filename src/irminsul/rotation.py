"""Moteur de rotations chiffrées — déterministe, défensif, ZÉRO chiffre inventé.

Chaque action de dégâts combine : coefficient de talent RÉEL (`talentstats`, sourcé/versionné)
× stat porteuse finale RÉELLE (`charstats`, depuis le scan) → `calculate_direct_hit` (`damage`).
Un coefficient ou une stat manquante ⇒ action **incomplète** (avertissement, jamais un faux dégât).
Le DPS n'est produit QUE si la rotation est complète et la durée valide.

Contrat : `rotation/1.0`. Bornes strictes (anti timestamps/durées négatifs, overlaps, NaN/inf,
rotation vide ou trop grande). Aucun chemin local renvoyé.
"""
from __future__ import annotations

import math
from typing import Any

from . import charstats, talentstats
from .damage import calculate_direct_hit

ROTATION_CONTRACT_VERSION = "rotation/1.0"

MAX_ACTIONS = 200          # borne anti-abus (pas de rotation non bornée)
MAX_TIME = 3600.0          # 1 h : borne dure de durée totale
DAMAGE_KINDS = frozenset({"normal_attack", "charged_attack", "plunging_attack", "skill", "burst"})
NON_DAMAGE_KINDS = frozenset({"swap", "wait"})
ALL_KINDS = DAMAGE_KINDS | NON_DAMAGE_KINDS


class RotationValidationError(ValueError):
    """Entrée de rotation invalide (structure/timeline) — jamais un calcul silencieux."""


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def _validate_enemy(enemy: Any) -> dict[str, float]:
    """Valide l'ennemi (audit Codex High #2) : champs finis et bornés avant la formule de coup.
    Empêche NaN dans le DPS et la division par zéro dans le multiplicateur de défense."""
    if enemy is None:
        return {"level": 100.0, "resistance": 0.10}
    if not isinstance(enemy, dict):
        raise RotationValidationError("enemy doit être un objet")
    level = enemy.get("level", 100)
    res = enemy.get("resistance", 0.10)
    if not _finite(level) or not (1 <= float(level) <= 200):
        raise RotationValidationError("enemy.level invalide (1..200 requis)")
    if not _finite(res) or not (-1.0 <= float(res) <= 3.0):
        raise RotationValidationError("enemy.resistance invalide (-1..3 requis)")
    return {"level": float(level), "resistance": float(res)}


def _validate_actions(actions: list[dict[str, Any]], team: set[str]) -> None:
    if not isinstance(actions, list) or not actions:
        raise RotationValidationError("rotation vide : au moins une action requise")
    if len(actions) > MAX_ACTIONS:
        raise RotationValidationError(f"trop d'actions (> {MAX_ACTIONS})")
    prev_end = 0.0
    for i, a in enumerate(actions):
        # Audit Codex Medium #3 : chaque action DOIT être un objet (pas None/str/int).
        if not isinstance(a, dict):
            raise RotationValidationError(f"action {i} : structure invalide (objet attendu)")
        kind = a.get("kind")
        if kind not in ALL_KINDS:
            raise RotationValidationError(f"action {i} : type inconnu {kind!r}")
        actor = a.get("actorId")
        if not isinstance(actor, str) or not actor.strip():
            raise RotationValidationError(f"action {i} : acteur manquant")
        if actor not in team:
            raise RotationValidationError(f"action {i} : acteur '{actor}' absent de l'équipe")
        start, dur = a.get("startTime"), a.get("duration")
        if not _finite(start) or start < 0:
            raise RotationValidationError(f"action {i} : startTime invalide (>= 0 requis)")
        if not _finite(dur) or dur < 0:
            raise RotationValidationError(f"action {i} : duration invalide (>= 0 requis)")
        if start + dur > MAX_TIME:
            raise RotationValidationError(f"action {i} : dépasse la borne de durée ({MAX_TIME}s)")
        # Séquence non chevauchante (une seule action à la fois — modèle mono-fil MVP).
        if start + 1e-9 < prev_end:
            raise RotationValidationError(
                f"action {i} : chevauchement (start {start} < fin précédente {prev_end})")
        prev_end = start + dur


def _actor_final_stats(key: str, cache: dict[str, Any]) -> dict[str, Any] | None:
    if key not in cache:
        try:
            payload = charstats.character_payload(key)
            ch = payload.get("character") if isinstance(payload, dict) else None
            cache[key] = ch.get("final_stats") if ch else None
        except Exception:  # noqa: BLE001 — frontière : jamais de crash, l'action sera incomplète
            cache[key] = None
    return cache[key]


def _cell(fs: dict[str, Any] | None, name: str) -> float | None:
    """Valeur finie d'une cellule (peut être partielle — usage crit avec défaut sûr)."""
    if not fs:
        return None
    c = fs.get(name)
    if isinstance(c, dict) and _finite(c.get("value")):
        return float(c["value"])
    return None


def _complete_cell(fs: dict[str, Any] | None, name: str) -> float | None:
    """Valeur d'une cellule SEULEMENT si `complete` (audit Codex High #1) : évite un faux DPS
    à partir de stats partielles (arme non supportée, main-stat non calculée…) avec valeurs finies."""
    if not fs:
        return None
    c = fs.get(name)
    if isinstance(c, dict) and c.get("complete") is True and _finite(c.get("value")):
        return float(c["value"])
    return None


def _compute_action_damage(
    a: dict[str, Any],
    fs: dict[str, Any] | None,
    enemy: dict[str, Any],
) -> dict[str, Any]:
    """Dégâts d'UNE action, ou incomplet+warning si une donnée réelle manque (jamais inventée)."""
    warnings: list[str] = []
    slot = a.get("talentSlot")
    label = a.get("talentLabel")
    level = a.get("talentLevel")
    actor = a["actorId"]

    coeff = None
    provenance: dict[str, Any] = {}
    if slot and label and isinstance(level, int) and not isinstance(level, bool):
        try:
            m = talentstats.talent_multiplier(actor, slot, label, level)
            if _finite(m.get("value")) and m.get("is_damage"):
                coeff = float(m["value"])
                p = m.get("provenance") or {}
                provenance = {"talent_source": p.get("source"), "talent_commit": p.get("source_commit")}
            else:
                warnings.append(f"coefficient '{label}' non-dégât ou non fini")
        except Exception:  # noqa: BLE001
            warnings.append(f"coefficient de talent introuvable ({slot}/{label} niv{level})")
    else:
        warnings.append("talent (slot/label/level) non renseigné")

    # High #1 : n'utiliser l'ATQ que si la cellule est COMPLÈTE (pas seulement finie) —
    # sinon la stat vient d'un build partiel et produirait un faux DPS marqué « complet ».
    atk = _complete_cell(fs, "atk")
    if atk is None:
        warnings.append("ATQ finale indisponible ou incomplète (stats partielles)")

    if coeff is None or atk is None:
        return {"actorId": actor, "kind": a.get("kind"), "complete": False,
                "damage": None, "warnings": warnings, "provenance": provenance}

    cr = (_cell(fs, "crit_rate_") or 5.0) / 100.0
    cd = (_cell(fs, "crit_dmg_") or 50.0) / 100.0
    # Bonus de dégâts : addition des %_dmg_ pertinents laissée à des tranches futures ;
    # ici 0 explicite (hypothèse affichée), jamais un bonus deviné.
    result = calculate_direct_hit(
        scaling=coeff, scaling_stat=atk, crit_rate=min(cr, 1.0), crit_damage=cd,
        enemy_level=int(enemy.get("level", 100)),
        enemy_resistance=float(enemy.get("resistance", 0.10)),
    )
    return {"actorId": actor, "kind": a.get("kind"), "complete": True,
            "damage": round(result.expected, 2),
            "damage_crit": round(result.crit, 2),
            "damage_noncrit": round(result.non_crit, 2),
            "coefficient": round(coeff, 6), "scaling_stat_atk": round(atk, 2),
            "warnings": warnings, "provenance": provenance}


def calculate_rotation(
    team: list[str],
    actions: list[dict[str, Any]],
    enemy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calcule une rotation. Retour = contrat `rotation/1.0` (voir docs)."""
    if not isinstance(team, list) or not team:
        raise RotationValidationError("équipe vide")
    # Medium #3 : membres d'équipe strictement des chaînes (pas de coercition str(1)->"1").
    if not all(isinstance(k, str) and k.strip() for k in team):
        raise RotationValidationError("membres d'équipe invalides (chaînes non vides requises)")
    team_set = set(team)
    _validate_actions(actions, team_set)
    enemy = _validate_enemy(enemy)  # High #2 : ennemi validé/borné avant toute formule

    cache: dict[str, Any] = {}
    resolved: list[dict[str, Any]] = []
    total_damage = 0.0
    by_char: dict[str, float] = {}
    duration = 0.0
    all_damage_complete = True
    assumptions = [
        "Modèle mono-fil : une action à la fois, séquence non chevauchante.",
        "Dégâts = coefficient de talent réel × ATQ finale réelle × coup direct ; hors buffs conditionnels et réactions (bonus de dégâts = 0 explicite en v1).",
        "Le DPS n'est calculé que si TOUTES les actions de dégâts sont complètes et la durée > 0.",
    ]

    for a in actions:
        end = float(a["startTime"]) + float(a["duration"])
        duration = max(duration, end)
        if a.get("kind") in NON_DAMAGE_KINDS:
            resolved.append({"actorId": a.get("actorId"), "kind": a.get("kind"),
                             "complete": True, "damage": None, "warnings": [], "provenance": {}})
            continue
        fs = _actor_final_stats(a["actorId"], cache)
        r = _compute_action_damage(a, fs, enemy)
        resolved.append(r)
        if r["complete"] and r["damage"] is not None:
            total_damage += r["damage"]
            by_char[r["actorId"]] = round(by_char.get(r["actorId"], 0.0) + r["damage"], 2)
        else:
            all_damage_complete = False

    complete = all_damage_complete and duration > 0
    warnings = sorted({w for r in resolved for w in r.get("warnings", [])})
    provenance = {"engine": "python", "contract": ROTATION_CONTRACT_VERSION,
                  "talent_data": talentstats.load_talents().get("version")}
    confidence = "high" if complete else ("medium" if total_damage > 0 else "low")

    out: dict[str, Any] = {
        "contract_version": ROTATION_CONTRACT_VERSION,
        "duration": round(duration, 3),
        "actions": resolved,
        "total_damage": round(total_damage, 2) if total_damage > 0 else None,
        "damage_by_character": by_char,
        "complete": complete,
        "assumptions": assumptions,
        "warnings": warnings,
        "provenance": provenance,
        "confidence": confidence,
    }
    # DPS UNIQUEMENT si complet et durée valide (jamais un faux DPS).
    if complete and duration > 0:
        out["average_damage_per_second"] = round(total_damage / duration, 2)
    else:
        out["average_damage_per_second"] = None
        out.setdefault("note", "rotation incomplète — DPS non calculé (données insuffisantes)")
    return out
