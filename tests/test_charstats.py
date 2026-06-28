"""Tests des statistiques de personnage dérivées du GOOD (artéfacts exacts,
stats de base signalées non calculées)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from irminsul import charstats
from irminsul.account_ipc import dispatch


def test_main_stat_table_matches_independent_reference() -> None:
    # Référence indépendante : valeurs publiques 5★ niveau 20 (in-game / GO).
    t = charstats.MAIN_STAT_5STAR_L20
    assert t["atk_"] == 46.6 and t["def_"] == 58.3
    assert t["critRate_"] == 31.1 and t["critDMG_"] == 62.2
    assert t["eleMas"] == 187.0 and t["enerRech_"] == 51.8
    assert t["hp"] == 4780.0 and t["atk"] == 311.0
    assert t["pyro_dmg_"] == 46.6 and t["physical_dmg_"] == 58.3


def test_artifact_totals_golden() -> None:
    arts = [
        {"setKey": "S", "slotKey": "flower", "rarity": 5, "level": 20, "mainStatKey": "hp",
         "substats": [{"key": "critRate_", "value": 3.5}]},
        {"setKey": "S", "slotKey": "circlet", "rarity": 5, "level": 20, "mainStatKey": "atk_",
         "substats": [{"key": "critRate_", "value": 7.0}, {"key": "critDMG_", "value": 14.0}]},
    ]
    out = charstats.artifact_stat_totals(arts)
    t = out["totals"]
    assert t["hp"] == 4780.0          # main 5★ L20
    assert t["atk_"] == 46.6
    assert t["critRate_"] == 10.5     # 3.5 + 7.0 substats
    assert t["critDMG_"] == 14.0
    assert out["uncomputed_main"] == []


def test_non_l20_main_is_flagged_not_invented() -> None:
    arts = [{"setKey": "S", "slotKey": "sands", "rarity": 4, "level": 16, "mainStatKey": "atk_",
             "substats": []}]
    out = charstats.artifact_stat_totals(arts)
    assert "atk_" not in out["totals"]       # pas approximé
    assert out["uncomputed_main"] and out["uncomputed_main"][0]["mainStatKey"] == "atk_"


def test_determinism_and_monotonicity() -> None:
    base = [{"setKey": "S", "slotKey": "sands", "rarity": 5, "level": 20, "mainStatKey": "atk_",
             "substats": [{"key": "critRate_", "value": 3.1}]}]
    more = [{"setKey": "S", "slotKey": "sands", "rarity": 5, "level": 20, "mainStatKey": "atk_",
             "substats": [{"key": "critRate_", "value": 3.1}, {"key": "critRate_", "value": 3.9}]}]
    a = charstats.artifact_stat_totals(base)["totals"]["critRate_"]
    b = charstats.artifact_stat_totals(more)["totals"]["critRate_"]
    assert b > a  # plus de substats crit ⇒ plus de CR
    assert charstats.artifact_stat_totals(base) == charstats.artifact_stat_totals(base)  # déterministe


def test_substat_non_finite_flagged_not_summed() -> None:
    # C3 (revue Codex) : substat NaN/non-numérique ignorée + signalée, jamais sommée.
    arts = [{"setKey": "S", "slotKey": "flower", "rarity": 5, "level": 20, "mainStatKey": "hp",
             "substats": [{"key": "atk_", "value": float("nan")},
                          {"key": "critRate_", "value": "abc"},
                          {"key": "critDMG_", "value": 7.0}]}]
    out = charstats.artifact_stat_totals(arts)
    assert "atk_" not in out["totals"]            # NaN non sommée
    assert out["totals"]["critDMG_"] == 7.0       # valide conservée
    assert len(out["anomalies"]) == 2             # NaN + non-numérique signalés


def test_uncomputed_main_marks_final_stat_incomplete() -> None:
    # C4 (revue Codex) : une stat principale d'artéfact non calculée se répercute sur
    # la complétude de la stat finale concernée (honnêteté, pas d'omission silencieuse).
    from irminsul import basestats
    base = basestats.character_base_stats("Furina", 90, 6).to_dict()
    uncomputed = [{"mainStatKey": "atk_", "rarity": 4, "level": 16, "set": "S", "slot": "sands"}]
    fs = charstats.compute_final_stats(base, {"atk_": 10.0}, uncomputed)
    assert "atk_" in fs["artifact_main_incomplete"]
    assert any("non calculée" in m for m in fs["atk"]["missing"])


def test_final_stats_never_emit_nan() -> None:
    # C3 : même avec un total corrompu, aucune stat finale ne sort NaN/inf.
    from irminsul import basestats
    base = basestats.character_base_stats("Furina", 90, 6).to_dict()
    fs = charstats.compute_final_stats(base, {"atk_": float("nan"), "critRate_": float("inf")})
    import math
    assert fs["atk"]["value"] is None or math.isfinite(fs["atk"]["value"])
    assert fs["crit_rate_"]["value"] is None or math.isfinite(fs["crit_rate_"]["value"])


# --- Intégration via le dispatch (compte importé temporaire) --- #
@pytest.fixture()
def imported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "proj"
    root.mkdir()
    monkeypatch.setenv("IRMINSUL_PROJECT_ROOT", str(root))
    good = tmp_path / "acc_GOOD.json"
    good.write_text(json.dumps({
        "format": "GOOD", "version": 3, "source": "Inventory_Kamera",
        "characters": [{"key": "Furina", "level": 90, "constellation": 0, "ascension": 6,
                        "talent": {"auto": 1, "skill": 6, "burst": 6}}],
        "weapons": [{"key": "FavoniusSword", "level": 90, "ascension": 6, "refinement": 1,
                     "location": "Furina", "lock": True, "id": 0}],
        "artifacts": [{"setKey": "GoldenTroupe", "slotKey": "circlet", "rarity": 5,
                       "mainStatKey": "critDMG_", "level": 20,
                       "substats": [{"key": "critRate_", "value": 7.0}], "location": "Furina"}],
        "materials": {"Mora": 1000},
    }), encoding="utf-8")
    dispatch("import-good", {"path": str(good)})


def test_characters_and_character_stats(imported: None) -> None:
    chars = dispatch("characters")
    assert chars["status"] == "ok" and "Furina" in chars["characters"]

    cs = dispatch("character-stats", {"key": "Furina"})
    assert cs["status"] == "ok"
    char = cs["character"]
    assert char["level"] == 90
    assert char["weapon"]["key"] == "FavoniusSword"
    assert char["artifact_stats"]["totals"]["critDMG_"] == 62.2  # main circlet 5★ L20
    assert char["artifact_stats"]["totals"]["critRate_"] == 7.0  # substat
    assert char["provenance"]["sha256"]                          # provenance présente

    # Stats de BASE désormais calculées automatiquement (sourcées genshin-db).
    base = char["base_stats"]
    assert base["supported"] is True
    assert round(base["hp"]) == 15307           # Furina L90A6, valeur jeu
    assert base["provenance"]["source_commit"]  # versionnée + sourcée
    assert base["ascension_stat_key"] == "critRate_"

    # Stats d'arme désormais calculées (FavoniusSword) → ATQ finale COMPLÈTE.
    wbs = char["weapon_base_stats"]
    assert wbs["supported"] is True and wbs["base_atk"] == 454.36  # Favonius L90A6 (valeur jeu)
    assert wbs["secondary_stat_key"] == "enerRech_"

    fs = char["final_stats"]
    assert fs is not None and fs["complete"] is True
    # crit DMG = 50 base + 62.2 (main artéfact) ; crit Rate = 5 + 7 (substat) + 19.2 (ascension)
    assert fs["crit_dmg_"]["value"] == 112.2
    assert fs["crit_rate_"]["value"] == 31.2
    # ATQ finale = base perso 243.96 + base arme 454.36 (pas d'ATQ%) → complète.
    assert fs["atk"]["complete"] is True and fs["atk"]["missing"] == []
    assert fs["atk"]["value"] == 698.32
    # Recharge = 100 base + 61.25 (stat secondaire Favonius).
    assert fs["enerRech_"]["value"] == 161.25

    # Passifs/conditionnels restent explicitement non pris en charge (jamais inventés).
    assert any("conditionnel" in u["reason"] for u in char["unsupported"])


def test_unsupported_base_falls_back_honestly(
    imported: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Si un perso est absent de la source de base : pas de stats finales inventées,
    # repli sur la saisie manuelle, signalé explicitement.
    from irminsul import basestats
    monkeypatch.setattr(
        basestats, "character_base_stats_payload",
        lambda *a, **k: {"supported": False, "reason": "absent de la source (test)"},
    )
    char = dispatch("character-stats", {"key": "Furina"})["character"]
    assert char["base_stats"]["supported"] is False
    assert char["final_stats"] is None
    assert any("stats de base" in u["item"] for u in char["unsupported"])


def test_character_not_found(imported: None) -> None:
    out = dispatch("character-stats", {"key": "Inconnu"})
    assert out["status"] == "not_found"


def test_character_stats_empty_without_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    monkeypatch.setenv("IRMINSUL_PROJECT_ROOT", str(root))
    assert dispatch("characters")["status"] == "empty"
    assert dispatch("character-stats", {"key": "X"})["status"] == "empty"
