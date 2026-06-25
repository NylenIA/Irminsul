"""Tests de classement et d'intégrité des sources.

L'ordre de confiance attendu : officiel HoYoverse (S) > theorycraft/simulation
reconnus (A) > données structurées et guides (B) > communautaire/spéculatif.
"""

from irminsul.config import ranked_sources, sources_config, tier_rank


def test_tier_rank_orders_official_above_theorycraft_above_data() -> None:
    assert tier_rank("S") < tier_rank("A") < tier_rank("B")
    assert tier_rank("S") == 0


def test_tier_rank_is_case_insensitive_and_safe() -> None:
    assert tier_rank("a") == tier_rank("A")
    assert tier_rank(None) >= len("SABCD") - 1  # tier manquant => classé en dernier
    assert tier_rank("ZZZ") >= 5                 # tier inconnu => classé en dernier


def test_sources_config_is_well_formed() -> None:
    config = sources_config()
    sources = config.get("sources", [])
    assert sources, "config/sources.yaml doit déclarer des sources"
    required = {"id", "name", "kind", "tier"}
    for source in sources:
        assert required <= set(source), f"champ manquant dans {source.get('id')}"
        assert tier_rank(source["tier"]) < len("SABCD"), f"tier invalide: {source['tier']}"


def test_ranked_sources_sorted_by_confidence() -> None:
    ranked = ranked_sources()
    ranks = [tier_rank(s.get("tier")) for s in ranked]
    assert ranks == sorted(ranks), "les sources doivent être triées par confiance"
    # Une source officielle (tier S) doit exister et arriver avant gcsim (tier A).
    names = [s.get("name", "") for s in ranked]
    official = next((i for i, s in enumerate(ranked) if s.get("tier") == "S"), None)
    gcsim_idx = next((i for i, n in enumerate(names) if "gcsim" in n.lower()), None)
    if official is not None and gcsim_idx is not None:
        assert official < gcsim_idx
