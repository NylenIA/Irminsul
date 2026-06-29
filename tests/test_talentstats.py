"""Tests des multiplicateurs de talents (talentstats) : golden (valeurs jeu via libellés),
slots/alias, classification dmg/buff, Voyageur par élément, bornes, robustesse, reproductibilité.
Aucune valeur inventée ; tout est sourcé genshin-db (tables + libellés localisés).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from irminsul import talentstats as ts


def test_golden_hutao_normal_1hit() -> None:
    # Hu Tao Attaque Normale, 1-Hit DMG : L1 = 46.9% (in-game), L10 = 83.6%.
    assert ts.talent_multiplier("HuTao", "normal", "1-Hit DMG", 1)["value"] == pytest.approx(0.468864)
    assert ts.talent_multiplier("HuTao", "normal", "1-Hit DMG", 10)["value"] == pytest.approx(0.836496)


def test_slot_aliases_equivalent() -> None:
    a = ts.talent_attributes("Furina", "burst", 10)
    b = ts.talent_attributes("Furina", "combat3", 10)
    assert a["supported"] and b["supported"] and a["slot"] == b["slot"] == "combat3"


def test_damage_vs_buff_classification() -> None:
    attrs = {a["label"]: a for a in ts.talent_attributes("HuTao", "skill", 10)["attributes"]}
    assert attrs["Blood Blossom DMG"]["is_damage"] is True
    assert attrs["ATK Increase"]["is_damage"] is False          # buff %, pas un coup
    assert attrs["Blood Blossom Duration"]["is_percent"] is False  # valeur brute (s)


def test_traveler_talents_differ_by_element() -> None:
    # Contrairement aux stats de base, les talents du Voyageur dépendent de l'élément.
    e = ts.talent_attributes("TravelerElectro", "skill", 10)
    h = ts.talent_attributes("TravelerHydro", "skill", 10)
    assert e["supported"] and h["supported"]
    assert ts.normalize_key("TravelerElectro") != ts.normalize_key("TravelerHydro")
    # au moins un libellé/valeur diffère
    assert e["attributes"] != h["attributes"]


def test_unknown_char_label_slot_explicit() -> None:
    assert ts.talent_attributes("NoSuchChar", "skill", 10)["supported"] is False
    assert ts.talent_attributes("HuTao", "inconnu", 10)["supported"] is False
    bad = ts.talent_multiplier("HuTao", "normal", "Libellé Inexistant", 10)
    assert bad["supported"] is False and "available" in bad


def test_level_bounds() -> None:
    assert ts.talent_attributes("HuTao", "normal", 0)["supported"] is False
    assert ts.talent_attributes("HuTao", "normal", 16)["supported"] is False
    assert ts.talent_attributes("HuTao", "normal", 15)["supported"] is True


def test_property_monotonic_damage_in_level() -> None:
    # Un multiplicateur de DÉGÂTS croît avec le niveau de talent.
    prev = -1.0
    for lvl in range(1, 16):
        v = ts.talent_multiplier("HuTao", "normal", "1-Hit DMG", lvl)["value"]
        assert v is not None and math.isfinite(v) and v > prev
        prev = v


def test_no_nan_emitted() -> None:
    for a in ts.talent_attributes("Neuvillette", "skill", 12)["attributes"]:
        assert a["value"] is None or math.isfinite(a["value"])


def test_provenance_reproducible_and_count() -> None:
    prov = ts.load_talents()["provenance"]
    assert prov["source"] == "genshin-db"
    assert prov.get("reproducible") is True
    assert prov["extracted_at"] == prov["source_commit_date"][:10]
    assert len(ts.supported_characters()) == prov["character_count"] >= 100


def test_extract_synthetic(tmp_path: Path) -> None:
    sd = tmp_path / "src" / "data"
    (sd / "stats").mkdir(parents=True)
    (sd / "English" / "talents").mkdir(parents=True)
    stats = {"testchar": {"combat1": {
        "param1": [round(0.4 + 0.03 * i, 6) for i in range(15)],
        "param2": [round(0.1 + 0.01 * i, 6) for i in range(15)],
        "param9": [25] * 15,
    }}}
    (sd / "stats" / "talents.json").write_text(json.dumps(stats), encoding="utf-8")
    en = {"combat1": {"name": "Test NA", "attributes": {"labels": [
        "1-Hit DMG|{param1:F1P}",
        "2-Part DMG|{param1:F1P}+{param2:F1P}",
        "Stamina Cost|{param9:F1}",
    ]}}}
    (sd / "English" / "talents" / "testchar.json").write_text(json.dumps(en), encoding="utf-8")

    out = ts.extract_talents_from_genshin_db(tmp_path, {"source_commit": "deadbeef"})
    attrs = {a["label"]: a for a in out["characters"]["testchar"]["combat1"]["attributes"]}
    assert attrs["1-Hit DMG"]["values"][0] == pytest.approx(0.4)       # param1 L1
    assert attrs["2-Part DMG"]["values"][0] == pytest.approx(0.5)      # param1+param2 (somme)
    assert attrs["Stamina Cost"]["is_percent"] is False                # F1 = brut
    assert attrs["1-Hit DMG"]["is_damage"] is True
