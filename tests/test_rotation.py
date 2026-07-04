"""TDD du moteur de rotations — validation stricte + calcul réel (aucun faux DPS).

Persos de test présents dans le scan ∩ talent ∩ basestats (Bennett).
"""
from __future__ import annotations

import math

import pytest

from irminsul.rotation import (
    ROTATION_CONTRACT_VERSION,
    RotationValidationError,
    calculate_rotation,
)

TEAM = ["Bennett"]


def _na(actor="Bennett", start=0.0, dur=1.0):
    return {"actorId": actor, "kind": "normal_attack", "startTime": start, "duration": dur,
            "talentSlot": "combat1", "talentLabel": "1-Hit DMG", "talentLevel": 10}


class TestValidation:
    def test_rotation_vide_rejetee(self) -> None:
        with pytest.raises(RotationValidationError, match="vide"):
            calculate_rotation(TEAM, [])

    def test_equipe_vide_rejetee(self) -> None:
        with pytest.raises(RotationValidationError, match="quipe vide"):
            calculate_rotation([], [_na()])

    def test_timestamp_negatif_rejete(self) -> None:
        with pytest.raises(RotationValidationError, match="startTime"):
            calculate_rotation(TEAM, [_na(start=-1.0)])

    def test_duree_negative_rejetee(self) -> None:
        with pytest.raises(RotationValidationError, match="duration"):
            calculate_rotation(TEAM, [_na(dur=-2.0)])

    def test_acteur_hors_equipe_rejete(self) -> None:
        with pytest.raises(RotationValidationError, match="absent de"):
            calculate_rotation(TEAM, [_na(actor="Ganyu")])

    def test_chevauchement_rejete(self) -> None:
        acts = [_na(start=0.0, dur=2.0), _na(start=1.0, dur=1.0)]
        with pytest.raises(RotationValidationError, match="chevauchement"):
            calculate_rotation(TEAM, acts)

    def test_type_inconnu_rejete(self) -> None:
        bad = _na(); bad["kind"] = "teleport"
        with pytest.raises(RotationValidationError, match="type inconnu"):
            calculate_rotation(TEAM, [bad])

    def test_nan_infinity_rejetes(self) -> None:
        with pytest.raises(RotationValidationError):
            calculate_rotation(TEAM, [_na(start=math.inf)])
        with pytest.raises(RotationValidationError):
            calculate_rotation(TEAM, [_na(dur=math.nan)])


class TestCalcul:
    def test_rotation_complete_produit_dps(self) -> None:
        acts = [_na(start=0.0, dur=1.0), _na(start=1.0, dur=1.0)]
        r = calculate_rotation(TEAM, acts)
        assert r["contract_version"] == ROTATION_CONTRACT_VERSION
        assert r["complete"] is True
        assert r["confidence"] == "high"
        assert r["total_damage"] > 0
        assert r["duration"] == 2.0
        # DPS = total / durée, seulement car complet.
        assert r["average_damage_per_second"] == pytest.approx(r["total_damage"] / 2.0, rel=1e-6)
        assert r["damage_by_character"]["Bennett"] == r["total_damage"]
        assert all(a["complete"] for a in r["actions"])

    def test_action_sans_talent_est_incomplete_sans_faux_dps(self) -> None:
        bad = {"actorId": "Bennett", "kind": "skill", "startTime": 0.0, "duration": 1.0}
        r = calculate_rotation(TEAM, [bad])
        assert r["complete"] is False
        assert r["average_damage_per_second"] is None       # jamais de faux DPS
        assert r["total_damage"] is None
        assert any("talent" in w for w in r["warnings"])
        assert "incomplète" in r.get("note", "")

    def test_coefficient_introuvable_incomplet(self) -> None:
        bad = _na(); bad["talentLabel"] = "Label Inexistant"
        r = calculate_rotation(TEAM, [bad])
        assert r["complete"] is False
        assert r["average_damage_per_second"] is None
        assert any("introuvable" in w or "coefficient" in w for w in r["warnings"])

    def test_swap_et_wait_comptent_la_duree_sans_degats(self) -> None:
        acts = [
            {"actorId": "Bennett", "kind": "swap", "startTime": 0.0, "duration": 0.5},
            _na(start=0.5, dur=1.0),
            {"actorId": "Bennett", "kind": "wait", "startTime": 1.5, "duration": 0.5},
        ]
        r = calculate_rotation(TEAM, acts)
        assert r["duration"] == 2.0
        assert r["complete"] is True
        assert r["total_damage"] > 0

    def test_provenance_et_hypotheses_presentes(self) -> None:
        r = calculate_rotation(TEAM, [_na()])
        assert r["provenance"]["contract"] == ROTATION_CONTRACT_VERSION
        assert any("coefficient de talent réel" in a for a in r["assumptions"])
        # provenance de talent remontée sur l'action complète
        act = r["actions"][0]
        assert act["provenance"].get("talent_source")
