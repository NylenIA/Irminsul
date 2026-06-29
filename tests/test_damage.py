from irminsul.damage import calculate_direct_hit, defense_multiplier, resistance_multiplier


def test_resistance_piecewise() -> None:
    assert resistance_multiplier(0.10) == 0.90
    assert resistance_multiplier(-0.20) == 1.10
    assert round(resistance_multiplier(0.80), 6) == round(1 / 4.2, 6)


def test_defense_multiplier_baseline() -> None:
    value = defense_multiplier(90, 100)
    assert 0.48 < value < 0.49


def test_direct_hit_expected_crit() -> None:
    result = calculate_direct_hit(
        scaling=2.0,
        scaling_stat=1000,
        damage_bonus=0.5,
        crit_rate=0.5,
        crit_damage=1.0,
        attacker_level=90,
        enemy_level=100,
        enemy_resistance=0.1,
    )
    assert result.raw_base == 2000
    assert result.crit == result.non_crit * 2
    assert result.expected == result.non_crit * 1.5


# --- Robustesse numérique (revue Codex §5.5) --- #
import math  # noqa: E402

import pytest  # noqa: E402


def test_rejects_non_finite_inputs() -> None:
    with pytest.raises(ValueError):
        calculate_direct_hit(scaling=float("nan"), scaling_stat=1000)
    with pytest.raises(ValueError):
        calculate_direct_hit(scaling=2.0, scaling_stat=float("inf"))
    with pytest.raises(ValueError):
        calculate_direct_hit(scaling=2.0, scaling_stat=1000, crit_damage=float("nan"))


def test_property_crit_rate_zero_no_average_crit() -> None:
    r = calculate_direct_hit(scaling=2.0, scaling_stat=2000, crit_rate=0.0, crit_damage=1.0)
    assert math.isfinite(r.expected)
    assert r.expected == r.non_crit  # CR=0 → aucun crit en moyenne


def test_property_higher_resistance_not_more_damage() -> None:
    lo = calculate_direct_hit(scaling=2.0, scaling_stat=2000, enemy_resistance=0.10)
    hi = calculate_direct_hit(scaling=2.0, scaling_stat=2000, enemy_resistance=0.50)
    assert hi.expected <= lo.expected


def test_property_higher_stat_not_less_damage() -> None:
    a = calculate_direct_hit(scaling=2.0, scaling_stat=2000)
    b = calculate_direct_hit(scaling=2.0, scaling_stat=3000)
    assert b.expected >= a.expected


def test_property_outputs_always_finite_nonnegative() -> None:
    r = calculate_direct_hit(scaling=2.5, scaling_stat=1800, damage_bonus=0.466,
                             crit_rate=0.7, crit_damage=1.4, enemy_resistance=-0.2)
    for v in (r.raw_base, r.non_crit, r.crit, r.expected):
        assert math.isfinite(v) and v >= 0


def test_rejects_non_finite_levels() -> None:
    # R2/C3.4 : les niveaux attaquant/ennemi doivent aussi être finis.
    with pytest.raises(ValueError):
        calculate_direct_hit(scaling=2.0, scaling_stat=1000, attacker_level=float("nan"))
    with pytest.raises(ValueError):
        calculate_direct_hit(scaling=2.0, scaling_stat=1000, enemy_level=float("inf"))
