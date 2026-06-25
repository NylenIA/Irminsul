from __future__ import annotations

from dataclasses import asdict, dataclass


def resistance_multiplier(resistance: float) -> float:
    if resistance < 0:
        return 1 - resistance / 2
    if resistance < 0.75:
        return 1 - resistance
    return 1 / (4 * resistance + 1)


def defense_multiplier(
    attacker_level: int,
    enemy_level: int,
    defense_reduction: float = 0.0,
    defense_ignore: float = 0.0,
) -> float:
    reduction = min(max(defense_reduction, 0.0), 0.99)
    ignore = min(max(defense_ignore, 0.0), 0.99)
    numerator = attacker_level + 100
    denominator = numerator + (enemy_level + 100) * (1 - reduction) * (1 - ignore)
    return numerator / denominator


@dataclass(slots=True)
class DirectHitResult:
    raw_base: float
    non_crit: float
    crit: float
    expected: float
    defense_multiplier: float
    resistance_multiplier: float
    expected_crit_multiplier: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def calculate_direct_hit(
    *,
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
) -> DirectHitResult:
    """Transparent direct-hit calculation.

    Percentages are decimals: 250% scaling = 2.5, 46.6% bonus = 0.466.
    Reaction multiplier is supplied explicitly to avoid guessing trigger direction.
    """
    if scaling < 0 or scaling_stat < 0:
        raise ValueError("scaling and scaling_stat must be non-negative")
    if amplifying_reaction_multiplier <= 0 or vulnerability_multiplier <= 0:
        raise ValueError("multipliers must be positive")

    crit_rate = min(max(crit_rate, 0.0), 1.0)
    crit_damage = max(crit_damage, 0.0)
    raw_base = scaling * scaling_stat + flat_base_damage
    def_mult = defense_multiplier(
        attacker_level, enemy_level, defense_reduction, defense_ignore
    )
    res_mult = resistance_multiplier(enemy_resistance)
    reaction = amplifying_reaction_multiplier * (1 + max(reaction_bonus, 0.0))
    non_crit = (
        raw_base
        * (1 + damage_bonus)
        * reaction
        * def_mult
        * res_mult
        * vulnerability_multiplier
    )
    crit = non_crit * (1 + crit_damage)
    expected_crit_multiplier = 1 + crit_rate * crit_damage
    expected = non_crit * expected_crit_multiplier
    return DirectHitResult(
        raw_base=raw_base,
        non_crit=non_crit,
        crit=crit,
        expected=expected,
        defense_multiplier=def_mult,
        resistance_multiplier=res_mult,
        expected_crit_multiplier=expected_crit_multiplier,
    )
