from __future__ import annotations

from dataclasses import asdict, dataclass

from .damage import resistance_multiplier

# Coefficient de niveau pour les réactions transformatives.
# Valeur de référence KQM pour un personnage niveau 90.
# Pour un autre niveau, fournir level_multiplier explicitement.
LEVEL_MULTIPLIER_LV90 = 1446.85

# Multiplicateurs de base des réactions transformatives (source : mécaniques KQM).
TRANSFORMATIVE_BASE = {
    "swirl": 0.6,
    "superconduct": 0.5,
    "electro-charged": 1.2,
    "overloaded": 2.0,
    "overload": 2.0,
    "shattered": 1.5,
    "shatter": 1.5,
    "burning": 0.25,
    "bloom": 2.0,
    "hyperbloom": 3.0,
    "burgeon": 3.0,
}

# Multiplicateurs de base des réactions amplifiantes.
AMPLIFYING_BASE = {
    "forward-vaporize": 2.0,
    "reverse-vaporize": 1.5,
    "forward-melt": 2.0,
    "reverse-melt": 1.5,
}

# Coefficients des réactions ADDITIVES (source : mécaniques KQM).
# Le bonus s'AJOUTE aux dégâts de base du talent (puis DMG%/crit/DEF/RES s'appliquent).
ADDITIVE_BASE = {
    "aggravate": 1.15,
    "spread": 1.25,
}


def transformative_em_bonus(elemental_mastery: float) -> float:
    """Bonus de Maîtrise pour une réaction transformative (formule KQM)."""
    em = max(elemental_mastery, 0.0)
    return 16 * em / (em + 2000)


def amplifying_em_bonus(elemental_mastery: float) -> float:
    """Bonus de Maîtrise pour une réaction amplifiante (formule KQM)."""
    em = max(elemental_mastery, 0.0)
    return 2.78 * em / (em + 1400)


def additive_em_bonus(elemental_mastery: float) -> float:
    """Bonus de Maîtrise pour une réaction additive (Aggravation/Propagation, KQM)."""
    em = max(elemental_mastery, 0.0)
    return 5.0 * em / (em + 1200)


@dataclass(slots=True)
class TransformativeResult:
    reaction: str
    base_multiplier: float
    level_multiplier: float
    em_bonus: float
    total_reaction_bonus: float
    resistance_multiplier: float
    damage: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(slots=True)
class AmplifyingResult:
    reaction: str
    base_multiplier: float
    em_bonus: float
    extra_bonus: float
    amplifying_multiplier: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(slots=True)
class AdditiveResult:
    reaction: str
    base_multiplier: float
    level_multiplier: float
    em_bonus: float
    extra_bonus: float
    base_bonus_damage: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


def transformative_reaction(
    *,
    reaction: str,
    elemental_mastery: float = 0.0,
    level_multiplier: float = LEVEL_MULTIPLIER_LV90,
    reaction_bonus: float = 0.0,
    enemy_resistance: float = 0.10,
) -> TransformativeResult:
    """Dégâts d'une réaction transformative, transparente et sans crit.

    `reaction_bonus` regroupe les bonus de réaction additifs hors Maîtrise
    (ex. set d'artefacts +40% Hyperbloom = 0.40). Les transformatives ne
    crit pas par défaut.
    """
    key = reaction.strip().lower()
    if key not in TRANSFORMATIVE_BASE:
        raise ValueError(
            f"Réaction transformative inconnue : {reaction!r}. "
            f"Options : {', '.join(sorted(set(TRANSFORMATIVE_BASE)))}"
        )
    if level_multiplier <= 0:
        raise ValueError("level_multiplier doit être positif")
    base = TRANSFORMATIVE_BASE[key]
    em_bonus = transformative_em_bonus(elemental_mastery)
    total_bonus = em_bonus + max(reaction_bonus, 0.0)
    res_mult = resistance_multiplier(enemy_resistance)
    damage = base * level_multiplier * (1 + total_bonus) * res_mult
    return TransformativeResult(
        reaction=key,
        base_multiplier=base,
        level_multiplier=level_multiplier,
        em_bonus=round(em_bonus, 4),
        total_reaction_bonus=round(total_bonus, 4),
        resistance_multiplier=round(res_mult, 4),
        damage=round(damage, 2),
    )


def amplifying_multiplier(
    *,
    reaction: str,
    elemental_mastery: float = 0.0,
    reaction_bonus: float = 0.0,
) -> AmplifyingResult:
    """Multiplicateur d'une réaction amplifiante (Vaporize / Melt).

    À injecter dans `calculate_direct_hit(amplifying_reaction_multiplier=...)`.
    `reaction_bonus` = bonus additifs hors Maîtrise (ex. set Crimson 4p = 0.15).
    """
    key = reaction.strip().lower()
    if key not in AMPLIFYING_BASE:
        raise ValueError(
            f"Réaction amplifiante inconnue : {reaction!r}. "
            f"Options : {', '.join(sorted(AMPLIFYING_BASE))}"
        )
    base = AMPLIFYING_BASE[key]
    em_bonus = amplifying_em_bonus(elemental_mastery)
    extra = max(reaction_bonus, 0.0)
    multiplier = base * (1 + em_bonus + extra)
    return AmplifyingResult(
        reaction=key,
        base_multiplier=base,
        em_bonus=round(em_bonus, 4),
        extra_bonus=round(extra, 4),
        amplifying_multiplier=round(multiplier, 4),
    )


def additive_reaction(
    *,
    reaction: str,
    elemental_mastery: float = 0.0,
    level_multiplier: float = LEVEL_MULTIPLIER_LV90,
    reaction_bonus: float = 0.0,
) -> AdditiveResult:
    """Bonus de base additif d'une réaction Aggravation/Propagation (KQM).

    base_bonus_damage = coef × level_multiplier × (1 + 5·EM/(EM+1200) + reaction_bonus).
    Ce montant s'AJOUTE aux dégâts de base du talent ; il est ensuite affecté par
    DMG%, crit, DEF et RES (à injecter via `flat_base_damage`). L'EM ne snapshot pas.
    """
    key = reaction.strip().lower()
    if key not in ADDITIVE_BASE:
        raise ValueError(
            f"Réaction additive inconnue : {reaction!r}. Options : {', '.join(sorted(ADDITIVE_BASE))}"
        )
    if level_multiplier <= 0:
        raise ValueError("level_multiplier doit être positif")
    base = ADDITIVE_BASE[key]
    em_bonus = additive_em_bonus(elemental_mastery)
    extra = max(reaction_bonus, 0.0)
    bonus = base * level_multiplier * (1 + em_bonus + extra)
    return AdditiveResult(
        reaction=key,
        base_multiplier=base,
        level_multiplier=level_multiplier,
        em_bonus=round(em_bonus, 4),
        extra_bonus=round(extra, 4),
        base_bonus_damage=round(bonus, 2),
    )
