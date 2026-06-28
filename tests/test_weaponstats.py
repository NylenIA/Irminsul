"""Tests des stats de base d'arme (weaponstats) : golden (valeurs jeu), unités de la
stat secondaire, caps de rareté, erreurs explicites, robustesse et reproductibilité.
Aucune valeur inventée ; tout est sourcé genshin-db.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from irminsul import weaponstats as ws

# Golden : ATQ de base + stat secondaire au niveau 90, ascension 6 — valeurs validées EN JEU.
GOLDEN_L90A6 = {
    "MistsplitterReforged": {"atk": 674.33, "sec": ("critDMG_", 44.1024)},
    "WolfsGravestone": {"atk": 608.07, "sec": ("atk_", 49.6152)},
    "TheCatch": {"atk": 509.61, "sec": ("enerRech_", 45.94)},
    "FavoniusSword": {"atk": 454.36, "sec": ("enerRech_", 61.2532)},
}


@pytest.mark.parametrize("key,exp", GOLDEN_L90A6.items())
def test_golden_l90a6(key: str, exp: dict) -> None:
    w = ws.weapon_base_stats(key, 90, 6)
    assert w.base_atk == exp["atk"]
    assert w.secondary_stat_key == exp["sec"][0]
    assert w.secondary_stat_value == exp["sec"][1]


def test_in_game_cross_check_rounds() -> None:
    assert round(ws.weapon_base_stats("MistsplitterReforged", 90, 6).base_atk) == 674
    assert round(ws.weapon_base_stats("WolfsGravestone", 90, 6).base_atk) == 608
    assert round(ws.weapon_base_stats("TheCatch", 90, 6).base_atk) == 510


def test_secondary_units_percent_vs_raw() -> None:
    # Pourcentage : Crit DMG en % (×100), pas en décimal.
    assert 40 < ws.weapon_base_stats("MistsplitterReforged", 90, 6).secondary_stat_value < 50
    # EM = valeur BRUTE (jamais ×100) : une arme EM doit donner une centaine d'EM, pas des milliers.
    em_weapons = [k for k in ws.supported_weapons()
                  if (ws.load_weaponstats()["weapons"][k].get("secondary_stat") == "eleMas")]
    assert em_weapons, "au moins une arme à Maîtrise attendue"
    w = ws.weapon_base_stats(em_weapons[0], 90, 6)
    assert w.secondary_stat_key == "eleMas" and 50 < w.secondary_stat_value < 300


def test_rarity_level_caps() -> None:
    # Arme 1★ (DullBlade) plafonnée au niveau 70 / ascension 4.
    p = ws.weapon_base_stats_payload("DullBlade", 90, 6)
    assert p["supported"] is False
    w = ws.weapon_base_stats("DullBlade", 70, 4)
    assert w.max_level == 70 and w.max_ascension == 4 and w.base_atk > 0


def test_fight_prop_none_has_no_secondary() -> None:
    none_weapons = [k for k in ws.supported_weapons()
                    if ws.load_weaponstats()["weapons"][k].get("secondary_stat") is None]
    assert none_weapons
    w = ws.weapon_base_stats(none_weapons[0], 70, 4)
    assert w.secondary_stat_key is None and w.secondary_stat_value == 0.0


@pytest.mark.parametrize("good,resolved", [
    ("MistsplitterReforged", "mistsplitterreforged"),
    ("TheCatch", "thecatch"),
    ("WolfsGravestone", "wolfsgravestone"),
])
def test_normalize_key(good: str, resolved: str) -> None:
    assert ws.normalize_key(good) == resolved


def test_unknown_weapon_explicit() -> None:
    with pytest.raises(ws.UnsupportedWeaponError):
        ws.weapon_base_stats("NoSuchWeapon", 90, 6)
    assert ws.weapon_base_stats_payload("NoSuchWeapon", 90, 6)["supported"] is False


def test_impossible_pair_rejected() -> None:
    with pytest.raises(ValueError, match="impossible"):
        ws.weapon_base_stats("MistsplitterReforged", 90, 0)
    with pytest.raises(ValueError):
        ws.weapon_base_stats("MistsplitterReforged", 91, 6)


# --- Propriétés --- #
WEAPON_PROGRESSION = [(1, 0), (20, 1), (40, 2), (50, 3), (60, 4), (70, 5), (80, 6), (90, 6)]


@pytest.mark.parametrize("key", ["MistsplitterReforged", "TheCatch", "FavoniusSword"])
def test_property_atk_monotonic(key: str) -> None:
    prev = -1.0
    for lvl, asc in WEAPON_PROGRESSION:
        w = ws.weapon_base_stats(key, lvl, asc)
        assert w.base_atk > prev
        prev = w.base_atk


def test_property_deterministic_and_finite() -> None:
    import math
    a = ws.weapon_base_stats("WolfsGravestone", 80, 6)
    b = ws.weapon_base_stats("WolfsGravestone", 80, 6)
    assert a.to_dict() == b.to_dict()
    assert math.isfinite(a.base_atk) and math.isfinite(a.secondary_stat_value)


def test_provenance_reproducible_and_count() -> None:
    data = ws.load_weaponstats()
    prov = data["provenance"]
    assert prov["source"] == "genshin-db"
    assert prov.get("reproducible") is True
    assert prov["extracted_at"] == prov["source_commit_date"][:10]
    assert len(ws.supported_weapons()) == prov["weapon_count"] >= 200


# --- Extraction sur source SYNTHÉTIQUE (pas la donnée gitignorée) --- #
def test_extract_weapons_synthetic(tmp_path: Path) -> None:
    sd = tmp_path / "src" / "data"
    (sd / "curve").mkdir(parents=True)
    (sd / "stats").mkdir(parents=True)
    curve = {str(lvl): {"GROW_CURVE_ATTACK_101": float(lvl), "GROW_CURVE_CRITICAL_101": float(lvl)}
             for lvl in range(1, 91)}
    (sd / "curve" / "weapons.json").write_text(json.dumps(curve), encoding="utf-8")
    stats = {"testsword": {
        "base": {"attack": 10.0, "specialized": 0.05},
        "curve": {"attack": "GROW_CURVE_ATTACK_101", "specialized": "GROW_CURVE_CRITICAL_101"},
        "specialized": "FIGHT_PROP_CRITICAL_HURT",
        "promotion": [{"maxlevel": 20, "attack": 0}, {"maxlevel": 40, "attack": 100},
                      {"maxlevel": 50, "attack": 200}, {"maxlevel": 60, "attack": 300},
                      {"maxlevel": 70, "attack": 400}, {"maxlevel": 80, "attack": 500},
                      {"maxlevel": 90, "attack": 600}],
    }}
    (sd / "stats" / "weapons.json").write_text(json.dumps(stats), encoding="utf-8")
    out = ws.extract_weapons_from_genshin_db(tmp_path, {"source_commit": "deadbeef"})
    assert out["provenance"]["weapon_count"] == 1
    w = out["weapons"]["testsword"]
    assert w["secondary_stat"] == "critDMG_" and w["max_level"] == 90 and w["max_ascension"] == 6
    # secondaire à 90 (courbe linéaire = 90) : 0.05 × 90 = 4.5 (décimal) → ×100 = 450 en convention GOOD.
    assert out["curves"]["GROW_CURVE_CRITICAL_101"]["90"] == 90.0
