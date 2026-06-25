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
