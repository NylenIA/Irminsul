from irminsul.leaks import DevelopmentStage, score_leak


def test_high_quality_leak_is_not_called_official() -> None:
    result = score_leak(
        provenance=5,
        evidence=5,
        corroboration=5,
        track_record=5,
        specificity=5,
        stage=DevelopmentStage.LATE_BETA,
    )
    assert result.grade == "A"
    assert "pas une vérité officielle" in result.authenticity_note


def test_conflicts_reduce_score() -> None:
    clean = score_leak(
        provenance=4, evidence=4, corroboration=4, track_record=4, specificity=4,
        stage=DevelopmentStage.LATE_BETA,
    )
    conflicted = score_leak(
        provenance=4, evidence=4, corroboration=4, track_record=4, specificity=4,
        stage=DevelopmentStage.LATE_BETA, conflict_penalty=20,
    )
    assert conflicted.score < clean.score
