"""Tests du pipeline d'import de compte GOOD (irminsul.account)."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from irminsul.account import (
    AllocationConflict,
    ExclusiveAllocator,
    build_overview,
    diff_snapshots,
    import_good,
    load_current,
    load_good,
    normalize,
    sha256_file,
    stable_weapon_id,
    validate_good,
)

GOOD_FIXTURE = {
    "format": "GOOD",
    "version": 3,
    "kamera_version": "1.4.3",
    "source": "Inventory_Kamera",
    "characters": [
        {"key": "Furina", "level": 90, "constellation": 0, "ascension": 6,
         "talent": {"auto": 1, "skill": 6, "burst": 6}},
        {"key": "Nahida", "level": 80, "constellation": 2, "ascension": 5,
         "talent": {"auto": 7, "skill": 9, "burst": 9}},
    ],
    "weapons": [
        {"key": "FavoniusSword", "level": 90, "ascension": 6, "refinement": 1,
         "location": "Furina", "lock": True, "id": 0},
        {"key": "DullBlade", "level": 1, "ascension": 0, "refinement": 1,
         "location": "", "lock": False, "id": 0},
        {"key": "DullBlade", "level": 1, "ascension": 0, "refinement": 1,
         "location": "", "lock": False, "id": 0},
        {"key": "AmenomaKageuchi", "level": 70, "ascension": 4, "refinement": 3,
         "location": "Traveler", "lock": False, "id": 5},
    ],
    "artifacts": [
        {"setKey": "GoldenTroupe", "slotKey": "flower", "rarity": 5, "mainStatKey": "hp",
         "level": 20, "substats": [{"key": "critRate_", "value": 3.9}], "location": "Furina",
         "lock": True, "id": 0},
        {"setKey": "DeepwoodMemories", "slotKey": "circlet", "rarity": 5,
         "mainStatKey": "critRate_", "level": 20, "substats": [], "location": "Nahida",
         "lock": False, "id": 0},
        {"setKey": "GoldenTroupe", "slotKey": "sands", "rarity": 5, "mainStatKey": "atk_",
         "level": 20, "substats": [], "location": "Traveler", "lock": False, "id": 0},
        {"setKey": "DeepwoodMemories", "slotKey": "goblet", "rarity": 5,
         "mainStatKey": "dendro_dmg_", "level": 16, "substats": [], "location": "",
         "lock": False, "id": 0},
    ],
    "materials": {"Mora": 1000, "CrownOfInsight": 2},
}


@pytest.fixture()
def good_file(tmp_path: Path) -> Path:
    path = tmp_path / "source_GOOD.json"
    path.write_text(json.dumps(GOOD_FIXTURE), encoding="utf-8")
    return path


@pytest.fixture()
def account_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isole data/account dans un dossier temporaire via IRMINSUL_PROJECT_ROOT."""
    root = tmp_path / "proj"
    root.mkdir()
    monkeypatch.setenv("IRMINSUL_PROJECT_ROOT", str(root))
    yield root
    # Restaure les droits d'écriture (la copie brute est mise en lecture seule).
    for p in root.rglob("*"):
        try:
            os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass


# --------------------------------------------------------------------------- #
def test_load_good_reads_json(good_file: Path) -> None:
    payload = load_good(good_file)
    assert payload["format"] == "GOOD"
    assert payload["version"] == 3
    assert len(payload["characters"]) == 2


def test_load_good_rejects_non_good(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"format": "NOPE"}), encoding="utf-8")
    with pytest.raises(ValueError, match="GOOD"):
        load_good(bad)


def test_import_creates_normalized_profile(good_file: Path, account_root: Path) -> None:
    import_good(good_file, snapshot_date="2026-06-26")
    current = account_root / "data" / "account" / "current"
    for name in ("account-profile", "characters", "weapons", "artifacts",
                 "materials", "equipment", "unresolved-data"):
        assert (current / f"{name}.json").exists(), name
    profile = json.loads((current / "account-profile.json").read_text(encoding="utf-8"))
    assert profile["counts"]["characters"] == 2
    assert profile["counts"]["unresolved_characters"] == 1


def test_import_honors_data_dir_env_desktop_scenario(
    good_file: Path, account_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scénario desktop : IRMINSUL_DATA_DIR (posée par Tauri) PRIME sur le repo.

    Le sidecar gelé tourne hors du dépôt : l'import doit atterrir dans le
    dossier de données de l'app, pas dans <repo>/data.
    """
    app_data = tmp_path / "appdata"
    monkeypatch.setenv("IRMINSUL_DATA_DIR", str(app_data))
    try:
        import_good(good_file, snapshot_date="2026-07-23")
        current = app_data / "account" / "current"
        assert (current / "account-profile.json").exists()
        # Rien n'a été écrit dans le project root simulé.
        assert not (account_root / "data" / "account" / "current").exists()
    finally:
        for p in app_data.rglob("*"):
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass


def test_import_is_idempotent(good_file: Path, account_root: Path) -> None:
    first = import_good(good_file, snapshot_date="2026-06-26")
    second = import_good(good_file, snapshot_date="2026-06-26")
    assert first["snapshot_created"] is True
    assert second["snapshot_created"] is False
    assert second["idempotent_skip"] is True
    manifest = json.loads((account_root / "data" / "account" / "manifest.json").read_text("utf-8"))
    assert len(manifest["imports"]) == 1  # pas de doublon


def test_raw_copy_preserved_and_matches_source(good_file: Path, account_root: Path) -> None:
    result = import_good(good_file, snapshot_date="2026-06-26")
    raw = Path(result["raw_copy"])
    assert raw.exists()
    assert sha256_file(raw) == sha256_file(good_file)  # contenu identique
    assert not os.access(raw, os.W_OK)  # copie en lecture seule


def test_duplicate_weapon_ids_get_unique_internal_ids(good_file: Path, account_root: Path) -> None:
    import_good(good_file, snapshot_date="2026-06-26")
    weapons = json.loads(
        (account_root / "data" / "account" / "current" / "weapons.json").read_text("utf-8")
    )["weapons"]
    internal_ids = list(weapons.keys())
    assert len(internal_ids) == len(set(internal_ids)) == 4  # 2 DullBlade id=0 restent distincts
    kamera_zero = [w for w in weapons.values() if w["kamera_id"] == 0]
    assert len(kamera_zero) == 3  # ids Kamera non fiables, mais ids internes uniques


def test_stable_weapon_id_distinguishes_duplicates() -> None:
    w = {"key": "DullBlade", "level": 1, "refinement": 1, "location": ""}
    assert stable_weapon_id(1, w) != stable_weapon_id(2, w)  # l'index sépare les copies


def test_traveler_kept_unresolved(good_file: Path, account_root: Path) -> None:
    import_good(good_file, snapshot_date="2026-06-26")
    unresolved = json.loads(
        (account_root / "data" / "account" / "current" / "unresolved-data.json").read_text("utf-8")
    )["unresolvedCharacters"]
    assert "Traveler" in unresolved
    assert len(unresolved["Traveler"]["weapons"]) == 1   # Amenoma
    assert "sands" in unresolved["Traveler"]["artifacts"]


def test_validation_flags_out_of_range() -> None:
    bad = {
        "format": "GOOD", "version": 3,
        "characters": [{"key": "X", "level": 999, "ascension": 9, "constellation": 7,
                        "talent": {"auto": 0, "skill": 6, "burst": 6}}],
        "weapons": [{"key": "W", "level": 0, "ascension": 0, "refinement": 9, "id": 1}],
        "artifacts": [{"setKey": "S", "slotKey": "wrong", "rarity": 9, "mainStatKey": "",
                       "level": 99, "substats": []}],
        "materials": {},
    }
    report = validate_good(bad)
    codes = {i["code"] for i in report["issues"]}
    assert {"char.level", "char.ascension", "char.const", "char.talent",
            "weapon.level", "weapon.refine", "art.slot", "art.rarity", "art.main"} <= codes
    assert report["counts_by_severity"]["ERROR"] >= 5


def test_validation_warns_duplicate_ids_and_unresolved(good_file: Path) -> None:
    report = validate_good(load_good(good_file))
    codes = {i["code"] for i in report["issues"]}
    assert "weapon.id_dup" in codes
    assert "equip.unresolved" in codes
    assert report["is_blocking"] is False


def test_normalized_items_keep_provenance() -> None:
    norm = normalize(GOOD_FIXTURE, source_path="x.json", sha="abc", snapshot_date="2026-06-26")
    any_weapon = next(iter(norm["weapons"]["weapons"].values()))
    assert "_provenance" in any_weapon
    assert any_weapon["_provenance"]["array"] == "weapons"
    assert isinstance(any_weapon["_provenance"]["index"], int)


def test_diff_detects_changes() -> None:
    old = normalize(GOOD_FIXTURE, source_path="x", sha="a", snapshot_date="2026-06-25")
    new_payload = json.loads(json.dumps(GOOD_FIXTURE))
    new_payload["characters"][1]["constellation"] = 4          # gain de constellation
    new_payload["characters"][1]["level"] = 90                 # level up
    new_payload["characters"].append(                          # nouveau perso
        {"key": "Kazuha", "level": 90, "constellation": 0, "ascension": 6,
         "talent": {"auto": 1, "skill": 9, "burst": 8}}
    )
    new = normalize(new_payload, source_path="x", sha="b", snapshot_date="2026-06-26")
    diff = diff_snapshots(old, new)
    assert "Kazuha" in diff["new_characters"]
    assert any(g["key"] == "Nahida" and g["to"] == 4 for g in diff["constellation_gains"])
    assert any(g["key"] == "Nahida" for g in diff["level_ups"])


def test_overview_reports_equipment_flags(good_file: Path, account_root: Path) -> None:
    import_good(good_file, snapshot_date="2026-06-26")
    overview = build_overview(load_current())
    assert overview["totals"]["characters"] == 2
    assert "Traveler" in overview["unresolved"]


# --------------------------------------------------------------------------- #
# Allocation exclusive (Abîme)
# --------------------------------------------------------------------------- #
def test_allocator_blocks_same_weapon_twice() -> None:
    alloc = ExclusiveAllocator()
    alloc.assign("w-001-FavoniusSword", "Furina")
    with pytest.raises(AllocationConflict):
        alloc.assign("w-001-FavoniusSword", "Nahida")


def test_allocator_blocks_same_artifact_twice() -> None:
    alloc = ExclusiveAllocator()
    alloc.assign("a-002-GoldenTroupe-sands", "TeamA")
    with pytest.raises(AllocationConflict):
        alloc.assign("a-002-GoldenTroupe-sands", "TeamB")


def test_allocator_allows_same_holder_reassign() -> None:
    alloc = ExclusiveAllocator()
    alloc.assign("w-001", "Furina")
    alloc.assign("w-001", "Furina")  # idempotent, pas de conflit
    assert alloc.owner("w-001") == "Furina"
