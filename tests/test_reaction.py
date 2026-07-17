import math

import pytest

from irminsul.reaction import (
    amplifying_em_bonus,
    amplifying_multiplier,
    transformative_em_bonus,
    transformative_reaction,
)


def test_transformative_no_em_baseline() -> None:
    # Overload niveau 90, 0 EM, RES 0 -> base * level_multiplier
    result = transformative_reaction(
        reaction="overloaded", elemental_mastery=0, enemy_resistance=0.0
    )
    assert result.base_multiplier == 2.0
    assert result.em_bonus == 0.0
    assert math.isclose(result.damage, 2.0 * 1446.85, rel_tol=1e-6)


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
