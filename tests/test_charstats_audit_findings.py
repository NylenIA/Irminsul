"""Régression des findings de l'audit Codex read-only sur le portage stats finales.

Chaque test encode un finding accepté (2 Medium + 1 Low) : donnée corrompue → anomalie
explicite (jamais un 0 silencieux ni un niveau « plausible » fabriqué) ; message d'erreur
sans chemin local.
"""
from __future__ import annotations

import pytest

from irminsul import basestats, charstats, weaponstats


class TestArtifactAnomalies:
    """Finding Medium #1 — value absente/mainStatKey absent ne doivent pas être zéroïsés en silence."""

    def test_substat_sans_valeur_est_une_anomalie(self) -> None:
        res = charstats.artifact_stat_totals(
            [{"setKey": "X", "slotKey": "flower", "substats": [{"key": "atk_", "value": None}]}]
        )
        assert "atk_" not in res["totals"]  # jamais additionné comme 0
        assert any("sans valeur" in a["reason"] for a in res["anomalies"])

    def test_artefact_sans_main_stat_est_une_anomalie(self) -> None:
        res = charstats.artifact_stat_totals(
            [{"setKey": "X", "slotKey": "flower", "mainStatKey": None, "substats": []}]
        )
        assert any("sans stat principale" in a["reason"] for a in res["anomalies"])

    def test_substat_valide_toujours_comptee(self) -> None:
        res = charstats.artifact_stat_totals(
            [{"setKey": "X", "slotKey": "sands", "mainStatKey": "atk_",
              "rarity": 5, "level": 20, "substats": [{"key": "critRate_", "value": 3.1}]}]
        )
        assert res["totals"]["critRate_"] == 3.1
        assert res["anomalies"] == []


class TestLevelFallback:
    """Finding Medium #2 — un niveau falsy réel (0) ne doit pas être promu en niveau 1."""

    def test_helper_conserve_zero_et_defaut_sur_none(self) -> None:
        assert charstats._level_or(0) == 0          # falsy réel conservé → rejeté en aval
        assert charstats._level_or(None) == 1        # absent → défaut
        assert charstats._level_or(90) == 90
        assert charstats._level_or(True) == 1        # bool jamais interprété comme niveau

    def test_basestats_rejette_niveau_zero_sans_fabriquer(self) -> None:
        payload = basestats.character_base_stats_payload("Mavuika", 0, 0)
        assert payload["supported"] is False
        assert "0" in payload["reason"]  # borne signalée, pas de stats fabriquées


class TestErrorMessageNoPathLeak:
    """Finding Low #3 — le message d'erreur données-absentes ne doit pas contenir de chemin absolu."""

    def test_basestats_message_sans_chemin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from pathlib import Path
        monkeypatch.setattr(basestats, "data_path", lambda: Path("Z:/absent/character-basestats.json"))
        with pytest.raises(FileNotFoundError) as exc:
            basestats.load_basestats()
        msg = str(exc.value)
        assert "Z:" not in msg and "/absent/" not in msg
        assert "character-basestats.json" in msg  # nom de fichier générique OK

    def test_weaponstats_message_sans_chemin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from pathlib import Path
        monkeypatch.setattr(weaponstats, "data_path", lambda: Path("Z:/absent/weapon-basestats.json"))
        with pytest.raises(FileNotFoundError) as exc:
            weaponstats.load_weaponstats()
        msg = str(exc.value)
        assert "Z:" not in msg and "/absent/" not in msg
