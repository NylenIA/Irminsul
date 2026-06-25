from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .damage import calculate_direct_hit as compute_direct_hit
from .enka import fetch_showcase
from .gcsim import run_gcsim as execute_gcsim
from .good import inspect_good_export as inspect_good
from .leaks import DevelopmentStage, score_leak as evaluate_leak
from .reaction import (
    amplifying_multiplier as compute_amplifying_multiplier,
    transformative_reaction as compute_transformative_reaction,
)
from .source_sync import rebuild_index, search_index, sync_repositories
from .status import system_status

mcp = FastMCP("Irminsul AI")


@mcp.tool()
def irminsul_status() -> dict[str, Any]:
    """Return local source versions, index age and readiness before current Genshin answers."""
    return system_status()


@mcp.tool()
def refresh_knowledge(sync_remote: bool = True) -> dict[str, Any]:
    """Refresh enabled public sources and rebuild the local search index."""
    result: dict[str, Any] = {}
    if sync_remote:
        result["sync"] = sync_repositories()
    result["index"] = rebuild_index()
    return result


@mcp.tool()
def search_knowledge(
    query: str,
    limit: int = 8,
    kinds: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Search indexed official archives, live data, KQM mechanics and simulation sources."""
    return search_index(query, limit=limit, kinds=kinds)


@mcp.tool()
def calculate_direct_hit(
    scaling: float,
    scaling_stat: float,
    flat_base_damage: float = 0.0,
    damage_bonus: float = 0.0,
    crit_rate: float = 0.05,
    crit_damage: float = 0.50,
    attacker_level: int = 90,
    enemy_level: int = 100,
    enemy_resistance: float = 0.10,
    defense_reduction: float = 0.0,
    defense_ignore: float = 0.0,
    amplifying_reaction_multiplier: float = 1.0,
    reaction_bonus: float = 0.0,
    vulnerability_multiplier: float = 1.0,
) -> dict[str, float]:
    """Calculate one transparent direct hit. All percentages are decimal values."""
    return compute_direct_hit(
        scaling=scaling,
        scaling_stat=scaling_stat,
        flat_base_damage=flat_base_damage,
        damage_bonus=damage_bonus,
        crit_rate=crit_rate,
        crit_damage=crit_damage,
        attacker_level=attacker_level,
        enemy_level=enemy_level,
        enemy_resistance=enemy_resistance,
        defense_reduction=defense_reduction,
        defense_ignore=defense_ignore,
        amplifying_reaction_multiplier=amplifying_reaction_multiplier,
        reaction_bonus=reaction_bonus,
        vulnerability_multiplier=vulnerability_multiplier,
    ).to_dict()


@mcp.tool()
def calculate_transformative_reaction(
    reaction: str,
    elemental_mastery: float = 0.0,
    level_multiplier: float = 1446.85,
    reaction_bonus: float = 0.0,
    enemy_resistance: float = 0.10,
) -> dict[str, Any]:
    """Damage of one transformative reaction (no crit). EM and bonuses are decimals.

    reaction: swirl, superconduct, electro-charged, overloaded, shattered,
    burning, bloom, hyperbloom or burgeon. level_multiplier defaults to lvl 90.
    """
    return compute_transformative_reaction(
        reaction=reaction,
        elemental_mastery=elemental_mastery,
        level_multiplier=level_multiplier,
        reaction_bonus=reaction_bonus,
        enemy_resistance=enemy_resistance,
    ).to_dict()


@mcp.tool()
def calculate_amplifying_multiplier(
    reaction: str,
    elemental_mastery: float = 0.0,
    reaction_bonus: float = 0.0,
) -> dict[str, Any]:
    """Amplifying multiplier (Vaporize/Melt) to feed into calculate_direct_hit.

    reaction: forward-vaporize, reverse-vaporize, forward-melt or reverse-melt.
    """
    return compute_amplifying_multiplier(
        reaction=reaction,
        elemental_mastery=elemental_mastery,
        reaction_bonus=reaction_bonus,
    ).to_dict()


@mcp.tool()
def score_leak(
    provenance: float,
    evidence: float,
    corroboration: float,
    track_record: float,
    specificity: float,
    stage: str = "unknown",
    conflict_penalty: float = 0.0,
) -> dict[str, object]:
    """Score one public, unconfirmed leak. This never converts a leak into official information."""
    try:
        parsed_stage = DevelopmentStage(stage)
    except ValueError:
        parsed_stage = DevelopmentStage.UNKNOWN
    return evaluate_leak(
        provenance=provenance,
        evidence=evidence,
        corroboration=corroboration,
        track_record=track_record,
        specificity=specificity,
        stage=parsed_stage,
        conflict_penalty=conflict_penalty,
    ).to_dict()


@mcp.tool()
def import_enka_showcase(uid: str, force: bool = False) -> dict[str, Any]:
    """Fetch one public Genshin showcase from Enka, caching it for the returned TTL."""
    return fetch_showcase(uid, force=force)


@mcp.tool()
def inspect_good_export(path: str) -> dict[str, Any]:
    """Inspect a local Genshin Optimizer GOOD export and summarize account inventory."""
    return inspect_good(path)


@mcp.tool()
def run_gcsim(config_path: str, open_viewer: bool = False) -> dict[str, Any]:
    """Run a local gcsim configuration and parse its headline DPS output."""
    return execute_gcsim(config_path, open_viewer=open_viewer)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
