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
