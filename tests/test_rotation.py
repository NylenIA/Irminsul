"""TDD du moteur de rotations — validation stricte + calcul réel (aucun faux DPS).

Persos de test présents dans le scan ∩ talent ∩ basestats (Mavuika).
"""
from __future__ import annotations

import math

import pytest

from irminsul.rotation import (
    ROTATION_CONTRACT_VERSION,
    RotationValidationError,
    calculate_rotation,
)

# Mavuika : présente dans scan ∩ talent ∩ basestats AVEC une ATQ finale COMPLÈTE
# (indispensable depuis le durcissement audit : un build partiel ne produit plus de DPS).
TEAM = ["Mavuika"]


def _na(actor="Mavuika", start=0.0, dur=1.0):
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

    def test_action_none_rejetee(self) -> None:
        # Audit Codex Medium #3 : structure invalide → erreur typée, pas AttributeError.
        with pytest.raises(RotationValidationError, match="structure invalide"):
            calculate_rotation(TEAM, [None])  # type: ignore[list-item]

    def test_membre_equipe_non_chaine_rejete(self) -> None:
        # team=[1] ne doit PAS être stringifié en "1" pour laisser passer un acteur "1".
        with pytest.raises(RotationValidationError, match="membres d'équipe"):
            calculate_rotation([1], [{**_na(), "actorId": "1"}])  # type: ignore[list-item]

    def test_enemy_resistance_nan_rejete(self) -> None:
        # Audit Codex High #2 : ennemi non fini → erreur, jamais un NaN dans le DPS.
        with pytest.raises(RotationValidationError, match="resistance"):
            calculate_rotation(TEAM, [_na()], enemy={"resistance": float("nan")})

    def test_enemy_level_hors_bornes_rejete(self) -> None:
        with pytest.raises(RotationValidationError, match="level"):
            calculate_rotation(TEAM, [_na()], enemy={"level": -290})
        with pytest.raises(RotationValidationError, match="resistance"):
            calculate_rotation(TEAM, [_na()], enemy={"resistance": "abc"})

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
        assert r["damage_by_character"]["Mavuika"] == r["total_damage"]
        assert all(a["complete"] for a in r["actions"])

    def test_action_sans_talent_est_incomplete_sans_faux_dps(self) -> None:
        bad = {"actorId": "Mavuika", "kind": "skill", "startTime": 0.0, "duration": 1.0}
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
            {"actorId": "Mavuika", "kind": "swap", "startTime": 0.0, "duration": 0.5},
            _na(start=0.5, dur=1.0),
            {"actorId": "Mavuika", "kind": "wait", "startTime": 1.5, "duration": 0.5},
        ]
        r = calculate_rotation(TEAM, acts)
        assert r["duration"] == 2.0
        assert r["complete"] is True
        assert r["total_damage"] > 0

    def test_atk_incomplete_ne_produit_pas_de_faux_dps(self) -> None:
        # Audit Codex High #1 : ATQ finie mais NON complète (build partiel) → action incomplète,
        # aucun DPS, malgré une valeur numérique présente.
        from irminsul.rotation import _compute_action_damage
        fs_partiel = {
            "complete": False,
            "atk": {"value": 1800.0, "complete": False, "missing": ["arme non prise en charge"]},
            "crit_rate_": {"value": 5.0, "complete": False, "missing": []},
            "crit_dmg_": {"value": 50.0, "complete": False, "missing": []},
        }
        r = _compute_action_damage(_na(), fs_partiel, {"level": 100, "resistance": 0.1})
        assert r["complete"] is False
        assert r["damage"] is None
        assert any("incomplète" in w or "partielles" in w for w in r["warnings"])

    def test_provenance_et_hypotheses_presentes(self) -> None:
        r = calculate_rotation(TEAM, [_na()])
        assert r["provenance"]["contract"] == ROTATION_CONTRACT_VERSION
        assert any("coefficient de talent réel" in a for a in r["assumptions"])
        # provenance de talent remontée sur l'action complète
        act = r["actions"][0]
        assert act["provenance"].get("talent_source")
