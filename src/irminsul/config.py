from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import project_root


# Hiérarchie de confiance des sources, du plus fiable (index 0) au moins fiable.
# S = officiel HoYoverse, A = theorycraft/simulation reconnus, B = données
# structurées et guides, C/D = communautaire faible ou spéculatif.
TIER_ORDER = ["S", "A", "B", "C", "D"]


def tier_rank(tier: str | None) -> int:
    """Rang de confiance d'un tier (0 = plus fiable). Tier inconnu = classé dernier."""
    if not isinstance(tier, str):
        return len(TIER_ORDER)
    try:
        return TIER_ORDER.index(tier.strip().upper())
    except ValueError:
        return len(TIER_ORDER)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def sources_config() -> dict[str, Any]:
    return load_yaml(project_root() / "config" / "sources.yaml")


def ranked_sources() -> list[dict[str, Any]]:
    """Sources locales et services externes triés par confiance décroissante.

    Sert à présenter et choisir une source : un tier S (officiel) prime
    toujours sur un tier A (theorycraft), lui-même sur un tier B (données),
    etc. À tier égal, on trie par nom pour un ordre déterministe.
    """
    config = sources_config()
    items: list[dict[str, Any]] = [
        *config.get("sources", []),
        *config.get("external_services", []),
    ]
    return sorted(items, key=lambda s: (tier_rank(s.get("tier")), str(s.get("name", ""))))


def defaults_config() -> dict[str, Any]:
    return load_yaml(project_root() / "config" / "defaults.yaml")


def player_profile() -> dict[str, Any]:
    return load_yaml(project_root() / "profiles" / "player.yaml")
