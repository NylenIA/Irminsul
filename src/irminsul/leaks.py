from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class DevelopmentStage(StrEnum):
    LIVE_OR_OFFICIAL = "official-live"
    LATE_BETA = "late-beta"
    EARLY_BETA = "early-beta"
    FAR_ROADMAP = "far-roadmap"
    UNKNOWN = "unknown"


STAGE_SCORE = {
    DevelopmentStage.LIVE_OR_OFFICIAL: 5,
    DevelopmentStage.LATE_BETA: 4,
    DevelopmentStage.EARLY_BETA: 2.5,
    DevelopmentStage.FAR_ROADMAP: 1,
    DevelopmentStage.UNKNOWN: 1.5,
}


@dataclass(slots=True)
class LeakScore:
    score: float
    grade: str
    label: str
    authenticity_note: str
    stability_note: str
    components: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _clamp_five(value: float) -> float:
    return min(max(value, 0.0), 5.0)


def score_leak(
    *,
    provenance: float,
    evidence: float,
    corroboration: float,
    track_record: float,
    specificity: float,
    stage: DevelopmentStage = DevelopmentStage.UNKNOWN,
    conflict_penalty: float = 0.0,
) -> LeakScore:
    components = {
        "provenance": _clamp_five(provenance) / 5 * 25,
        "evidence": _clamp_five(evidence) / 5 * 25,
        "corroboration": _clamp_five(corroboration) / 5 * 20,
        "track_record": _clamp_five(track_record) / 5 * 15,
        "specificity": _clamp_five(specificity) / 5 * 10,
        "stage_stability": STAGE_SCORE[stage],
    }
    score = max(0.0, min(100.0, sum(components.values()) - min(max(conflict_penalty, 0), 20)))
    if score >= 85:
        grade, label = "A", "très solide pour un leak"
    elif score >= 70:
        grade, label = "B", "crédible mais modifiable"
    elif score >= 50:
        grade, label = "C", "plausible, confirmation insuffisante"
    elif score >= 30:
        grade, label = "D", "faible fiabilité"
    else:
        grade, label = "E", "rumeur ou spéculation"

    authenticity_note = (
        "Le score estime la crédibilité de cette publication précise, pas une vérité officielle."
    )
    if stage in {DevelopmentStage.EARLY_BETA, DevelopmentStage.FAR_ROADMAP}:
        stability_note = "Même authentique, le contenu a une forte probabilité de changer avant sortie."
    elif stage == DevelopmentStage.LATE_BETA:
        stability_note = "Le contenu est plus avancé, mais des changements restent possibles."
    elif stage == DevelopmentStage.LIVE_OR_OFFICIAL:
        stability_note = "Ce stade ne devrait normalement plus être traité comme un leak."
    else:
        stability_note = "Stade inconnu : appliquer une marge d'incertitude élevée."

    return LeakScore(
        score=round(score, 1),
        grade=grade,
        label=label,
        authenticity_note=authenticity_note,
        stability_note=stability_note,
        components={key: round(value, 1) for key, value in components.items()},
    )
