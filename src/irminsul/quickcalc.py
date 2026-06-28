"""Moteur de calcul rapide déterministe (Phase 3), sourcé via le registre des
mécaniques. Réutilise `damage.calculate_direct_hit` et `reaction` (amplifiantes,
additives, transformatrices) — aucune réimplémentation. Renvoie le détail complet
et traçable (« Voir le calcul ») : entrées, multiplicateurs, réaction, DEF, RES,
crit, dégâts, version de mécanique, source et confiance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .damage import calculate_direct_hit
from .paths import project_root
from .reaction import (
    ADDITIVE_BASE,
    AMPLIFYING_BASE,
    TRANSFORMATIVE_BASE,
    additive_reaction,
    amplifying_multiplier,
    transformative_reaction,
)

VALID_STATUS = {"verified", "probable", "experimental", "unknown"}


def registry_path() -> Path:
    """Localise le registre : embarqué dans le sidecar gelé (PyInstaller, sys._MEIPASS),
    sinon dans le dépôt en dev/tests. Voyage donc AVEC le moteur, pas dans l'app-data."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = project_root()
    return base / "data" / "mechanics" / "source-registry.json"


def load_registry() -> dict[str, Any]:
    return json.loads(registry_path().read_text(encoding="utf-8"))


def mechanics_payload() -> dict[str, Any]:
    return {"status": "ok", "registry": load_registry()}


def _f(params: dict[str, Any], key: str, default: float) -> float:
    val = params.get(key, default)
    try:
        return float(val)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"paramètre '{key}' invalide: {val!r}") from exc


def _registry_detail(used: list[str]) -> tuple[list[dict[str, Any]], Any]:
    reg = load_registry()
    idx = {m["id"]: m for m in reg.get("mechanics", [])}
    detail = [
        {"id": i, "status": idx[i]["status"], "confidence": idx[i]["confidence"],
         "sources": idx[i]["sources"], "verified_at": idx[i].get("verified_at")}
        for i in used if i in idx
    ]
    return detail, reg.get("version")


def quickcalc_payload(params: dict[str, Any]) -> dict[str, Any]:
    """Calcule un coup direct (optionnellement amplifié/additif) et, pour une réaction
    transformatrice, l'instance correspondante — avec détail + traçabilité du registre."""
    if "scaling" not in params or "stat" not in params:
        raise ValueError("paramètres requis: 'scaling' et 'stat'")
    scaling = _f(params, "scaling", 0.0)
    stat = _f(params, "stat", 0.0)
    em = _f(params, "em", 0.0)
    reaction_bonus = _f(params, "reaction_bonus", 0.0)
    resistance = _f(params, "resistance", 0.1)

    amp = 1.0
    amp_detail: dict[str, Any] | None = None
    additive_bonus = 0.0
    additive_detail: dict[str, Any] | None = None
    transformative: dict[str, Any] | None = None
    mechanics_used = ["outgoing_damage", "defense_multiplier", "resistance_multiplier"]

    reaction = params.get("reaction")
    if reaction:
        key = str(reaction).strip().lower()
        if key in AMPLIFYING_BASE:
            a = amplifying_multiplier(reaction=key, elemental_mastery=em, reaction_bonus=reaction_bonus)
            amp = a.amplifying_multiplier
            amp_detail = a.to_dict()
            mechanics_used.append("amplifying_reaction")
        elif key in ADDITIVE_BASE:
            ad = additive_reaction(reaction=key, elemental_mastery=em, reaction_bonus=reaction_bonus)
            additive_bonus = ad.base_bonus_damage
            additive_detail = ad.to_dict()
            mechanics_used.append("additive_reaction")
        elif key in TRANSFORMATIVE_BASE:
            t = transformative_reaction(
                reaction=key, elemental_mastery=em, reaction_bonus=reaction_bonus,
                enemy_resistance=resistance,
            )
            transformative = t.to_dict()
            mechanics_used.append("transformative_reaction")
        else:
            raise ValueError(f"réaction inconnue: {reaction!r}")

    result = calculate_direct_hit(
        scaling=scaling,
        scaling_stat=stat,
        flat_base_damage=_f(params, "flat", 0.0) + additive_bonus,
        damage_bonus=_f(params, "damage_bonus", 0.0),
        crit_rate=_f(params, "crit_rate", 0.05),
        crit_damage=_f(params, "crit_damage", 0.5),
        attacker_level=int(_f(params, "attacker_level", 90)),
        enemy_level=int(_f(params, "enemy_level", 100)),
        enemy_resistance=resistance,
        defense_reduction=_f(params, "defense_reduction", 0.0),
        defense_ignore=_f(params, "defense_ignore", 0.0),
        amplifying_reaction_multiplier=amp,
    )
    detail, version = _registry_detail(mechanics_used)
    return {
        "status": "ok",
        "result": result.to_dict(),
        "amplifying": amp_detail,
        "additive": additive_detail,
        "transformative": transformative,
        "mechanics_used": mechanics_used,
        "mechanics_detail": detail,
        "registry_version": version,
        "inputs": {k: params.get(k) for k in (
            "scaling", "stat", "damage_bonus", "crit_rate", "crit_damage",
            "resistance", "reaction", "em", "attacker_level", "enemy_level",
        ) if k in params},
    }
