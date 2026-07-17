from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field

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

# --- Réactions lunaires (Luna I / 5.8+) -------------------------------------
# Multiplicateurs de base (KQM Lunar Reaction Guide,
# https://keqingmains.com/misc/lunar-reactions/ ; corroborés wiki/game8) :
# Lunar-Charged 1.8 (dégâts Electro) ; Lunar-Crystallize 1.6 (dégâts Géo,
# pas d'ICD global). Lunar-Bloom EXCLU : multiplicateur non confirmé par KQM
# (mécanique à cœurs différente) — aucune valeur inventée.
LUNAR_BASE = {
    "lunar-charged": 1.8,
    "lunar-crystallize": 1.6,
}

# Pondérations d'agrégation multi-participants, classées par dégâts personnels
# décroissants : 100 % / 50 % / 1/12 / 1/12 (KQM + Icy Veins, concordants).
LUNAR_CONTRIBUTION_WEIGHTS = (1.0, 0.5, 1.0 / 12.0, 1.0 / 12.0)

# Multiplicateurs de base des réactions amplifiantes.
AMPLIFYING_BASE = {
    "forward-vaporize": 2.0,
    "reverse-vaporize": 1.5,
    "forward-melt": 2.0,
    "reverse-melt": 1.5,
}

# Coefficients des réactions ADDITIVES (source : mécaniques KQM ; porté de la
# branche phase3, commit d61803b, formules inchangées). Le bonus s'AJOUTE aux
# dégâts de base du talent (puis DMG%/crit/DEF/RES s'appliquent).
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


def lunar_em_bonus(elemental_mastery: float) -> float:
    """Bonus de Maîtrise pour une réaction lunaire : 6·EM/(EM+2000).

    Constantes résolues exactement sur les 3 points publiés (Icy Veins,
    « Lunar-Charged DMG Formula Clarified ») : 500 EM → +120 %,
    1000 EM → +200 %, 1500 EM → +257,14 % ; structure analogue au
    16·EM/(EM+2000) des transformatives.
    """
    em = max(elemental_mastery, 0.0)
    return 6 * em / (em + 2000)


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


@dataclass(slots=True)
class LunarChargedResult:
    reaction: str
    base_multiplier: float
    level_multiplier: float
    resistance_multiplier: float
    contributors: list[dict[str, float]] = field(default_factory=list)
    damage: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_LUNAR_CONTRIBUTOR_KEYS = frozenset(
    {"elemental_mastery", "crit_rate", "crit_damage", "base_dmg_bonus", "reaction_bonus"}
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
    DMG%, crit, DEF et RES (à injecter via `flat_base_damage` du coup direct).
    """
    key = reaction.strip().lower()
    if key not in ADDITIVE_BASE:
        raise ValueError(
            f"Réaction additive inconnue : {reaction!r}. "
            f"Options : {', '.join(sorted(ADDITIVE_BASE))}"
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


def lunar_reaction(
    *,
    reaction: str,
    contributors: Sequence[Mapping[str, float]],
    level_multiplier: float = LEVEL_MULTIPLIER_LV90,
    enemy_resistance: float = 0.10,
) -> LunarChargedResult:
    """Dégâts moyens d'une réaction lunaire multi-participants (ignore la DEF).

    Réactions : lunar-charged (1.8, Electro) · lunar-crystallize (1.6, Géo).
    Formule par contributeur (KQM Lunar Reaction Guide) :
    base × mult_niveau × (1 + base_dmg_bonus) × (1 + reaction_bonus + 6·EM/(EM+2000))
    × espérance de crit (1 + taux×dégâts crit, stats du contributeur).
    Agrégation par dégâts personnels décroissants : 100 % / 50 % / 1/12 / 1/12,
    puis multiplicateur de RES de l'ennemi (élément de la réaction — au choix
    de l'appelant via enemy_resistance).

    Chaque contributeur : {elemental_mastery, crit_rate, crit_damage,
    base_dmg_bonus, reaction_bonus} (tous optionnels, défaut 0).

    Hypothèses/limites (documentées, pas de fausse précision) :
    - valeur MOYENNE : le jeu détermine le crit affiché via le meilleur
      contributeur, sans effet sur l'espérance calculée ici ;
    - l'ICD de déclenchement (LC ~2 s ; LCrys sans ICD global) relève du
      modèle de rotation, pas d'ici ;
    - « Elevation » et bonus Moonsign se passent via base_dmg_bonus /
      reaction_bonus du contributeur concerné ;
    - lunar-bloom ABSENT : multiplicateur non confirmé (pas de valeur inventée).
    """
    key = reaction.strip().lower()
    if key not in LUNAR_BASE:
        raise ValueError(
            f"Réaction lunaire inconnue : {reaction!r}. "
            f"Options : {', '.join(sorted(LUNAR_BASE))}"
        )
    if not contributors:
        raise ValueError("contributors ne peut pas être vide (1 à 4 participants)")
    if len(contributors) > len(LUNAR_CONTRIBUTION_WEIGHTS):
        raise ValueError(
            f"Au plus {len(LUNAR_CONTRIBUTION_WEIGHTS)} contributeurs (équipe Genshin) ; "
            f"reçu {len(contributors)}"
        )
    if level_multiplier <= 0:
        raise ValueError("level_multiplier doit être positif")

    base = LUNAR_BASE[key]
    computed: list[dict[str, float]] = []
    for i, raw in enumerate(contributors):
        unknown = set(raw) - _LUNAR_CONTRIBUTOR_KEYS
        if unknown:
            raise ValueError(
                f"Clés inconnues pour le contributeur {i} : {sorted(unknown)}. "
                f"Attendues : {sorted(_LUNAR_CONTRIBUTOR_KEYS)}"
            )
        em_bonus = lunar_em_bonus(float(raw.get("elemental_mastery", 0.0)))
        crit_rate = min(max(float(raw.get("crit_rate", 0.0)), 0.0), 1.0)
        crit_damage = max(float(raw.get("crit_damage", 0.0)), 0.0)
        expected_crit = 1.0 + crit_rate * crit_damage
        base_dmg_bonus = max(float(raw.get("base_dmg_bonus", 0.0)), 0.0)
        reaction_bonus = max(float(raw.get("reaction_bonus", 0.0)), 0.0)
        personal = (
            base
            * level_multiplier
            * (1.0 + base_dmg_bonus)
            * (1.0 + reaction_bonus + em_bonus)
            * expected_crit
        )
        computed.append(
            {
                "em_bonus": round(em_bonus, 4),
                "expected_crit_multiplier": round(expected_crit, 4),
                "base_dmg_bonus": round(base_dmg_bonus, 4),
                "reaction_bonus": round(reaction_bonus, 4),
                "personal_damage": personal,
            }
        )

    computed.sort(key=lambda c: c["personal_damage"], reverse=True)
    res_mult = resistance_multiplier(enemy_resistance)
    total = 0.0
    for rank, entry in enumerate(computed):
        weight = LUNAR_CONTRIBUTION_WEIGHTS[rank]
        weighted = entry["personal_damage"] * weight
        total += weighted
        entry["weight"] = round(weight, 6)
        entry["weighted_damage"] = round(weighted * res_mult, 2)
        entry["personal_damage"] = round(entry["personal_damage"], 2)

    return LunarChargedResult(
        reaction=key,
        base_multiplier=base,
        level_multiplier=level_multiplier,
        resistance_multiplier=round(res_mult, 4),
        contributors=computed,
        damage=round(total * res_mult, 2),
    )


def lunar_charged_reaction(
    *,
    contributors: Sequence[Mapping[str, float]],
    level_multiplier: float = LEVEL_MULTIPLIER_LV90,
    enemy_resistance: float = 0.10,
) -> LunarChargedResult:
    """Compat : Lunar-Charged via `lunar_reaction` (contrat sidecar existant)."""
    return lunar_reaction(
        reaction="lunar-charged",
        contributors=contributors,
        level_multiplier=level_multiplier,
        enemy_resistance=enemy_resistance,
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
