import json

import pytest

from irminsul.good import inspect_good_export


def test_good_summary(tmp_path) -> None:
    path = tmp_path / "account.json"
    path.write_text(
        json.dumps(
            {
                "format": "GOOD",
                "version": 1,
                "source": "test",
                "characters": [{"key": "Furina"}],
                "weapons": [{"key": "FavoniusSword"}, {"key": "FavoniusSword"}],
                "artifacts": [
                    {"setKey": "GoldenTroupe", "location": "Furina"},
                    {"setKey": "GoldenTroupe", "location": ""},
                ],
                "materials": {"Mora": 1000},
            }
        ),
        encoding="utf-8",
    )
    result = inspect_good_export(path)
    assert result["counts"]["characters"] == 1
    assert result["weapon_inventory"]["FavoniusSword"] == 2
    assert result["artifact_sets"]["GoldenTroupe"] == 2


def test_good_rejects_wrong_format(tmp_path) -> None:
    """Un JSON valide mais sans format GOOD doit être refusé clairement."""
    path = tmp_path / "not-good.json"
    path.write_text(json.dumps({"format": "SomethingElse", "characters": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="GOOD"):
        inspect_good_export(path)


def test_good_rejects_malformed_json(tmp_path) -> None:
    """Un fichier JSON corrompu ne doit pas faire planter sans message."""
    path = tmp_path / "broken.json"
    path.write_text("{ this is not : valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        inspect_good_export(path)


def test_good_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        inspect_good_export("does/not/exist-GOOD.json")
