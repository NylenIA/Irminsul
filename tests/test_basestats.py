"""Tests des stats de base perso (basestats) : golden (valeurs jeu), unités de la
stat d'ascension, résolution de clés, erreurs explicites, et propriétés
(monotonie/déterminisme/bornes). Aucune valeur inventée ; tout est sourcé genshin-db.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from irminsul import basestats as bs

# --- Golden : valeurs déterministes du fichier committé, validées en jeu. --- #
# (HP/ATQ/DÉF au niveau 90, ascension 6.)
GOLDEN_L90A6 = {
    "KamisatoAyaka": {"hp": 12858.21, "atk": 342.03, "def": 783.93,
                      "asc": ("critDMG_", 38.4)},
    "HuTao": {"hp": 15552.31, "atk": 106.43, "def": 876.15, "asc": ("critDMG_", 38.4)},
    "Diluc": {"hp": 12980.67, "atk": 334.85, "def": 783.93, "asc": ("critRate_", 19.2)},
    "Bennett": {"hp": 12397.4, "atk": 191.16, "def": 771.25, "asc": ("enerRech_", 26.67)},
}


@pytest.mark.parametrize("key,exp", GOLDEN_L90A6.items())
def test_golden_l90a6(key: str, exp: dict) -> None:
    b = bs.character_base_stats(key, 90, 6)
    assert b.hp == exp["hp"]
    assert b.atk == exp["atk"]
    assert b.defense == exp["def"]
    assert b.ascension_stat_key == exp["asc"][0]
    assert b.ascension_stat_value == exp["asc"][1]


def test_in_game_cross_check_rounds() -> None:
    # Référence indépendante : valeurs PV affichées en jeu (arrondi entier).
    assert round(bs.character_base_stats("KamisatoAyaka", 90, 6).hp) == 12858
    assert round(bs.character_base_stats("HuTao", 90, 6).hp) == 15552
    assert round(bs.character_base_stats("Bennett", 90, 6).hp) == 12397
    # Hu Tao : ATQ de base notoirement basse.
    assert round(bs.character_base_stats("HuTao", 90, 6).atk) == 106


def test_ascension_stat_units() -> None:
    # EM = valeur BRUTE (pas ×100) ; pourcentages convertis (×100).
    assert bs.character_base_stats("Lisa", 90, 6).ascension_stat_value == 96.0
    assert bs.character_base_stats("Nahida", 90, 6).ascension_stat_value == 115.2
    assert bs.character_base_stats("Lisa", 90, 6).ascension_stat_key == "eleMas"
    # 0.384 (décimal) → 38.4 (%) pour les Dégâts Crit d'ascension d'Ayaka.
    assert bs.character_base_stats("KamisatoAyaka", 90, 6).ascension_stat_value == 38.4


def test_convert_specialized_value_units() -> None:
    assert bs.convert_specialized_value("eleMas", 96) == 96.0           # brut
    assert bs.convert_specialized_value("critDMG_", 0.384) == pytest.approx(38.4)
    assert bs.convert_specialized_value("atk_", 0.18) == pytest.approx(18.0)


def test_specialized_mapping_complete() -> None:
    # Toutes les stats d'ascension du jeu doivent être mappées (sinon extraction casse).
    assert bs.specialized_to_good("FIGHT_PROP_ELEMENT_MASTERY") == "eleMas"
    assert bs.specialized_to_good("FIGHT_PROP_ATTACK_PERCENT") == "atk_"
    assert bs.specialized_to_good("FIGHT_PROP_CRITICAL_HURT") == "critDMG_"
    assert bs.specialized_to_good("FIGHT_PROP_FIRE_ADD_HURT") == "pyro_dmg_"


@pytest.mark.parametrize("good,resolved", [
    ("KamisatoAyaka", "kamisatoayaka"),
    ("HuTao", "hutao"),
    ("RaidenShogun", "raidenshogun"),
    ("TravelerElectro", "aether"),
    ("TravelerAnemo", "aether"),
    ("Aether", "aether"),
    ("Lumine", "aether"),
])
def test_normalize_key(good: str, resolved: str) -> None:
    assert bs.normalize_key(good) == resolved


def test_traveler_variants_identical() -> None:
    a = bs.character_base_stats("TravelerElectro", 90, 6)
    b = bs.character_base_stats("TravelerGeo", 90, 6)
    assert (a.hp, a.atk, a.defense) == (b.hp, b.atk, b.defense)


def test_unknown_character_is_explicit_not_invented() -> None:
    with pytest.raises(bs.UnsupportedCharacterError):
        bs.character_base_stats("PersoQuiNexistePas", 90, 6)
    payload = bs.character_base_stats_payload("PersoQuiNexistePas", 90, 6)
    assert payload["supported"] is False and payload["reason"]


def test_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        bs.character_base_stats("HuTao", 0, 6)
    with pytest.raises(ValueError):
        bs.character_base_stats("HuTao", 91, 6)
    with pytest.raises(ValueError):
        bs.character_base_stats("HuTao", 90, 7)


def test_payload_shape_supported() -> None:
    p = bs.character_base_stats_payload("HuTao", 90, 6)
    assert p["supported"] is True
    assert {"hp", "atk", "def", "crit_rate_", "crit_dmg_",
            "ascension_stat_key", "ascension_stat_value", "provenance"} <= set(p)
    assert p["def"] == 876.15  # "defense" exposé sous la clé "def"


# --- Propriétés (déterministes, sans hypothesis) --- #
@pytest.mark.parametrize("key", ["HuTao", "KamisatoAyaka", "Bennett", "Nahida"])
def test_property_monotonic_in_level(key: str) -> None:
    prev_hp = prev_atk = prev_def = -1.0
    for lvl in (1, 20, 40, 60, 80, 90):
        b = bs.character_base_stats(key, lvl, 0)
        assert b.hp > prev_hp and b.atk > prev_atk and b.defense > prev_def
        prev_hp, prev_atk, prev_def = b.hp, b.atk, b.defense


def test_property_ascension_only_increases_stats() -> None:
    # À niveau égal, monter d'ascension n'abaisse jamais une stat de base.
    prev = (-1.0, -1.0, -1.0)
    for asc in range(0, 7):
        b = bs.character_base_stats("HuTao", 90, asc)
        cur = (b.hp, b.atk, b.defense)
        assert all(c >= p for c, p in zip(cur, prev))
        prev = cur


def test_property_deterministic_and_non_negative() -> None:
    a = bs.character_base_stats("Furina", 80, 5)
    b = bs.character_base_stats("Furina", 80, 5)
    assert a.to_dict() == b.to_dict()
    assert a.hp > 0 and a.atk > 0 and a.defense > 0


def test_supported_count_matches_provenance() -> None:
    data = bs.load_basestats()
    assert len(bs.supported_characters()) == data["provenance"]["character_count"]
    assert len(bs.supported_characters()) >= 119


def test_provenance_versioned_and_sourced() -> None:
    prov = bs.load_basestats()["provenance"]
    assert prov["source"] == "genshin-db"
    assert prov["source_commit"] and len(prov["source_commit"]) >= 7
    assert "courbe" in prov["formula"] or "curve" in prov["formula"]
    assert prov["confidence"] == "high"
    assert prov["formula_sources"]  # au moins une source de formule (rang B)
    # La provenance voyage dans chaque résultat.
    assert bs.character_base_stats("HuTao", 90, 6).provenance["source_commit"]


# --- Extraction : testée sur une source SYNTHÉTIQUE (pas la donnée gitignorée) --- #
def test_extract_from_genshin_db_synthetic(tmp_path: Path) -> None:
    sd = tmp_path / "src" / "data"
    (sd / "curve").mkdir(parents=True)
    (sd / "stats").mkdir(parents=True)
    # Courbe minimale niveaux 1..90 (linéaire) pour 2 colonnes.
    curve = {str(lvl): {"GROW_CURVE_HP_S5": float(lvl), "GROW_CURVE_ATTACK_S5": float(lvl)}
             for lvl in range(1, 91)}
    (sd / "curve" / "characters.json").write_text(json.dumps(curve), encoding="utf-8")
    stats = {"testchar": {
        "base": {"hp": 100.0, "attack": 10.0, "defense": 5.0, "critrate": 0.05, "critdmg": 0.5},
        "curve": {"hp": "GROW_CURVE_HP_S5", "attack": "GROW_CURVE_ATTACK_S5",
                  "defense": "GROW_CURVE_HP_S5"},
        "specialized": "FIGHT_PROP_CRITICAL_HURT",
        "promotion": [{"maxlevel": 20, "hp": 0, "attack": 0, "defense": 0, "specialized": 0}]
                     + [{"maxlevel": m, "hp": 1000, "attack": 50, "defense": 100,
                         "specialized": 0.384} for m in (40, 50, 60, 70, 80, 90)],
    }}
    (sd / "stats" / "characters.json").write_text(json.dumps(stats), encoding="utf-8")

    out = bs.extract_from_genshin_db(tmp_path, {"source_commit": "deadbeef"})
    assert out["provenance"]["character_count"] == 1
    c = out["characters"]["testchar"]
    assert c["ascension_stat"] == "critDMG_"
    # ascension convertie (×100) : 0.384 → 38.4
    assert c["promotion"][6]["ascension"] == pytest.approx(38.4)
    # niveau 90 sur courbe linéaire (=90) : 100×90 + 1000 (promo asc6) = 10000.
    assert out["curves"]["GROW_CURVE_HP_S5"]["90"] == 90.0
