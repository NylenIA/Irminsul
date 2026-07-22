import math

import pytest

from irminsul.reaction import (
    amplifying_em_bonus,
    amplifying_multiplier,
    transformative_em_bonus,
    transformative_reaction,
)


def test_transformative_no_em_baseline() -> None:
    # Overload niveau 90, 0 EM, RES 0 -> base * level_multiplier (base 5.2+ = 2.75)
    result = transformative_reaction(
        reaction="overloaded", elemental_mastery=0, enemy_resistance=0.0
    )
    assert result.base_multiplier == 2.75
    assert result.em_bonus == 0.0
    assert math.isclose(result.damage, 2.75 * 1446.85, rel_tol=1e-6)


def test_transformative_5_2_buffed_bases() -> None:
    # Garde anti-regression sur les buffs patch 5.2 (source KQM TCL + comparatif 5.2).
    bases = {
        r: transformative_reaction(reaction=r, enemy_resistance=0.0).base_multiplier
        for r in ("superconduct", "electro-charged", "overloaded", "shattered", "swirl", "burning")
    }
    assert bases == {
        "superconduct": 1.5,
        "electro-charged": 2.0,
        "overloaded": 2.75,
        "shattered": 3.0,
        "swirl": 0.6,  # inchange par 5.2
        "burning": 0.25,  # inchange
    }


def test_transformative_em_bonus_formula() -> None:
    assert math.isclose(transformative_em_bonus(2000), 8.0, rel_tol=1e-9)
    # Hyperbloom base 3.0
    result = transformative_reaction(
        reaction="hyperbloom", elemental_mastery=100, enemy_resistance=0.10
    )
    assert result.base_multiplier == 3.0
    assert result.total_reaction_bonus == result.em_bonus
    assert result.resistance_multiplier == 0.90


def test_unknown_transformative_raises() -> None:
    with pytest.raises(ValueError):
        transformative_reaction(reaction="meltdown")


def test_amplifying_multiplier_forward_vaporize() -> None:
    result = amplifying_multiplier(reaction="forward-vaporize", elemental_mastery=0)
    assert result.base_multiplier == 2.0
    assert math.isclose(result.amplifying_multiplier, 2.0, rel_tol=1e-9)


def test_amplifying_em_and_bonus_stack() -> None:
    em_bonus = amplifying_em_bonus(200)
    result = amplifying_multiplier(
        reaction="reverse-melt", elemental_mastery=200, reaction_bonus=0.15
    )
    expected = 1.5 * (1 + em_bonus + 0.15)
    assert math.isclose(result.amplifying_multiplier, round(expected, 4), rel_tol=1e-6)


def test_unknown_amplifying_raises() -> None:
    with pytest.raises(ValueError):
        amplifying_multiplier(reaction="vaporize")


# --- Réactions lunaires (Lunar-Charged) --------------------------------------

def test_lunar_em_bonus_published_datapoints() -> None:
    # Points publiés (Icy Veins) qui fixent 6*EM/(EM+2000) :
    from irminsul.reaction import lunar_em_bonus

    assert math.isclose(lunar_em_bonus(500), 1.2, rel_tol=1e-9)  # +120 %
    assert math.isclose(lunar_em_bonus(1000), 2.0, rel_tol=1e-9)  # +200 %
    assert math.isclose(lunar_em_bonus(1500), 18 / 7, rel_tol=1e-9)  # +257,14 %
    assert lunar_em_bonus(-50) == 0.0


def test_lunar_charged_single_contributor_baseline() -> None:
    from irminsul.reaction import lunar_charged_reaction

    result = lunar_charged_reaction(
        contributors=[{"elemental_mastery": 1000}], enemy_resistance=0.0
    )
    # 1.8 * 1446.85 * (1 + 2.0), sans crit ni bonus.
    assert result.base_multiplier == 1.8
    assert math.isclose(result.damage, 1.8 * 1446.85 * 3.0, rel_tol=1e-6)
    assert result.contributors[0]["weight"] == 1.0


def test_lunar_charged_aggregation_orders_by_damage() -> None:
    from irminsul.reaction import lunar_charged_reaction

    # Fourni dans le MAUVAIS ordre : le tri par dégâts doit poser les poids 1 / 0.5.
    weak = {"elemental_mastery": 0}      # facteur (1+0) = 1
    strong = {"elemental_mastery": 2000}  # facteur (1+3) = 4
    result = lunar_charged_reaction(contributors=[weak, strong], enemy_resistance=0.0)
    k = 1.8 * 1446.85
    assert math.isclose(result.damage, k * (4.0 + 0.5 * 1.0), rel_tol=1e-6)
    assert result.contributors[0]["em_bonus"] == 3.0  # le fort est premier


def test_lunar_charged_four_contributors_weights() -> None:
    from irminsul.reaction import lunar_charged_reaction

    result = lunar_charged_reaction(
        contributors=[{}, {}, {}, {}], enemy_resistance=0.0
    )
    k = 1.8 * 1446.85
    assert math.isclose(result.damage, k * (1 + 0.5 + 1 / 12 + 1 / 12), rel_tol=1e-6)


def test_lunar_charged_expected_crit_and_resistance() -> None:
    from irminsul.reaction import lunar_charged_reaction

    # crit_rate clampé à 1.0 ; RES 10 % par défaut -> x0.90.
    result = lunar_charged_reaction(
        contributors=[{"crit_rate": 1.5, "crit_damage": 1.0}]
    )
    k = 1.8 * 1446.85
    assert result.contributors[0]["expected_crit_multiplier"] == 2.0
    assert result.resistance_multiplier == 0.90
    assert math.isclose(result.damage, k * 2.0 * 0.90, rel_tol=1e-6)


def test_lunar_charged_validation_errors() -> None:
    from irminsul.reaction import lunar_charged_reaction

    with pytest.raises(ValueError):
        lunar_charged_reaction(contributors=[])
    with pytest.raises(ValueError):
        lunar_charged_reaction(contributors=[{}] * 5)
    with pytest.raises(ValueError):
        lunar_charged_reaction(contributors=[{"em": 100}])  # clé inconnue
    with pytest.raises(ValueError):
        lunar_charged_reaction(contributors=[{}], level_multiplier=0)


def test_lunar_charged_via_engine_dispatch() -> None:
    # Le sidecar expose la méthode : même résultat que l'appel direct.
    from irminsul.engine_dispatch import CANONICAL_METHODS, dispatch

    assert "lunar_charged_reaction" in CANONICAL_METHODS
    payload = {"contributors": [{"elemental_mastery": 1000}], "enemy_resistance": 0.0}
    via_dispatch = dispatch("lunar_charged_reaction", payload)
    assert math.isclose(via_dispatch["damage"], 1.8 * 1446.85 * 3.0, rel_tol=1e-6)


def test_lunar_crystallize_base_and_generic_api() -> None:
    from irminsul.reaction import lunar_reaction

    # LCrys : base 1.6 (KQM, corroboré), même formule EM, mêmes poids.
    result = lunar_reaction(
        reaction="lunar-crystallize",
        contributors=[{"elemental_mastery": 1000}],
        enemy_resistance=0.0,
    )
    assert result.reaction == "lunar-crystallize"
    assert result.base_multiplier == 1.6
    assert math.isclose(result.damage, 1.6 * 1446.85 * 3.0, rel_tol=1e-6)
    # Wrapper de compat : identique à l'appel générique.
    from irminsul.reaction import lunar_charged_reaction

    a = lunar_charged_reaction(contributors=[{"elemental_mastery": 500}])
    b = lunar_reaction(reaction="lunar-charged", contributors=[{"elemental_mastery": 500}])
    assert a.to_dict() == b.to_dict()
    with pytest.raises(ValueError):
        lunar_reaction(reaction="lunar-bloom", contributors=[{}])  # exclu v1


# --- Réactions additives (Aggravation / Propagation) --------------------------

def test_additive_baselines_and_em_formula() -> None:
    from irminsul.reaction import additive_em_bonus, additive_reaction

    # Goldens historiques phase3 (d61803b) : EM 0, niveau 90.
    agg = additive_reaction(reaction="aggravate")
    spr = additive_reaction(reaction="spread")
    assert math.isclose(agg.base_bonus_damage, 1663.88, abs_tol=0.01)
    assert math.isclose(spr.base_bonus_damage, 1808.56, abs_tol=0.01)
    # Formule EM : 5·EM/(EM+1200) -> 2.5 à 1200 EM.
    assert math.isclose(additive_em_bonus(1200), 2.5, rel_tol=1e-9)
    # Monotone en EM.
    assert additive_em_bonus(400) < additive_em_bonus(800) < additive_em_bonus(1600)
    with pytest.raises(ValueError):
        additive_reaction(reaction="quicken")


def test_additive_composes_with_direct_hit_flat_base() -> None:
    from irminsul.damage import calculate_direct_hit
    from irminsul.reaction import additive_reaction

    detail = additive_reaction(reaction="aggravate", elemental_mastery=300)
    base = calculate_direct_hit(scaling=2.0, scaling_stat=1500, crit_rate=0, crit_damage=0)
    boosted = calculate_direct_hit(
        scaling=2.0,
        scaling_stat=1500,
        crit_rate=0,
        crit_damage=0,
        flat_base_damage=detail.base_bonus_damage,
    )
    # Le bonus additif augmente la BASE (puis modifié par DEF/RES identiques).
    assert boosted.expected > base.expected
    # L'écart correspond exactement au bonus × DEF × RES (structure raw_base + flat).
    assert math.isclose(
        boosted.raw_base - base.raw_base, detail.base_bonus_damage, abs_tol=1e-9
    )


def test_additive_via_engine_dispatch() -> None:
    from irminsul.engine_dispatch import CANONICAL_METHODS, dispatch

    assert "additive_reaction" in CANONICAL_METHODS
    out = dispatch("additive_reaction", {"reaction": "spread", "elemental_mastery": 0})
    assert math.isclose(out["base_bonus_damage"], 1808.56, abs_tol=0.01)
