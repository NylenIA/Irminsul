"""Moteur de calcul rapide déterministe (Phase 3), sourcé via le registre des
mécaniques. Réutilise `damage.calculate_direct_hit` et `reaction` — aucune
réimplémentation. Renvoie le détail complet (« Voir le calcul »).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .damage import calculate_direct_hit
from .paths import project_root
from .reaction import amplifying_multiplier

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


def quickcalc_payload(params: dict[str, Any]) -> dict[str, Any]:
    """Calcule un coup direct (optionnellement amplifié) avec détail + traçabilité."""
    if "scaling" not in params or "stat" not in params:
        raise ValueError("paramètres requis: 'scaling' et 'stat'")
    scaling = _f(params, "scaling", 0.0)
    stat = _f(params, "stat", 0.0)

    reaction = params.get("reaction")
    amp = 1.0
    amp_detail: dict[str, Any] | None = None
    mechanics_used = ["outgoing_damage", "defense_multiplier", "resistance_multiplier"]
    if reaction:
        a = amplifying_multiplier(
            reaction=str(reaction),
            elemental_mastery=_f(params, "em", 0.0),
            reaction_bonus=_f(params, "reaction_bonus", 0.0),
        )
        amp = a.amplifying_multiplier
        amp_detail = a.to_dict()
        mechanics_used.append("amplifying_reaction")

    result = calculate_direct_hit(
        scaling=scaling,
        scaling_stat=stat,
        flat_base_damage=_f(params, "flat", 0.0),
        damage_bonus=_f(params, "damage_bonus", 0.0),
        crit_rate=_f(params, "crit_rate", 0.05),
        crit_damage=_f(params, "crit_damage", 0.5),
        attacker_level=int(_f(params, "attacker_level", 90)),
        enemy_level=int(_f(params, "enemy_level", 100)),
        enemy_resistance=_f(params, "resistance", 0.1),
        defense_reduction=_f(params, "defense_reduction", 0.0),
        defense_ignore=_f(params, "defense_ignore", 0.0),
        amplifying_reaction_multiplier=amp,
    )
    return {
        "status": "ok",
        "result": result.to_dict(),
        "amplifying": amp_detail,
        "mechanics_used": mechanics_used,
        "registry_version": load_registry().get("version"),
        "inputs": {k: params.get(k) for k in (
            "scaling", "stat", "damage_bonus", "crit_rate", "crit_damage",
            "resistance", "reaction", "em") if k in params},
    }
