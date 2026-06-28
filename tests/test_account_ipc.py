"""Tests du pont IPC moteur compte (sortie JSON pure, sans donnée factice)."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from irminsul import account_ipc


def _run(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = account_ipc.main(argv)
    return code, json.loads(buf.getvalue())


@pytest.fixture()
def account_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    monkeypatch.setenv("IRMINSUL_PROJECT_ROOT", str(root))
    return root


def _good(path: Path) -> Path:
    path.write_text(json.dumps({
        "format": "GOOD", "version": 3, "source": "Inventory_Kamera",
        "characters": [{"key": "Furina", "level": 90, "constellation": 0,
                        "ascension": 6, "talent": {"auto": 1, "skill": 6, "burst": 6}}],
        "weapons": [{"key": "FavoniusSword", "level": 90, "ascension": 6,
                     "refinement": 1, "location": "Furina", "lock": True, "id": 0}],
        "artifacts": [], "materials": {"Mora": 1000},
    }), encoding="utf-8")
    return path


def test_empty_before_import(account_root: Path) -> None:
    code, out = _run(["overview"])
    assert code == 0 and out["status"] == "empty"  # jamais de donnée inventée
    code, out = _run(["profile"])
    assert out["status"] == "empty"


def test_import_then_profile_and_overview(tmp_path: Path, account_root: Path) -> None:
    good = _good(tmp_path / "acc_GOOD.json")
    code, out = _run(["import-good", str(good)])
    assert code == 0 and out["status"] == "ok"
    assert out["import"]["counts"]["characters"] == 1
    assert set(out["import"]["validation"]) == {"INFO", "WARNING", "ERROR", "BLOCKING"}

    code, prof = _run(["profile"])
    assert prof["status"] == "ok"
    assert prof["profile"]["good_version"] == 3
    assert prof["profile"]["sha256"]  # provenance présente

    code, ov = _run(["overview"])
    assert ov["status"] == "ok"
    assert ov["overview"]["totals"]["characters"] == 1


def test_roster_lists_characters_weapons_sets(tmp_path: Path, account_root: Path) -> None:
    good = _good(tmp_path / "acc_GOOD.json")
    _run(["import-good", str(good)])
    code, out = _run(["roster"])
    assert code == 0 and out["status"] == "ok"
    r = out["roster"]
    assert r["characters"][0]["key"] == "Furina"
    assert r["characters"][0]["weapon"]["key"] == "FavoniusSword"
    assert any(w["key"] == "FavoniusSword" for w in r["weapons"])


def test_roster_empty_without_import(account_root: Path) -> None:
    code, out = _run(["roster"])
    assert code == 0 and out["status"] == "empty"


def test_unknown_command_returns_error() -> None:
    code, out = _run(["nope"])
    assert code == 2 and "error" in out


def test_import_missing_path_is_explicit() -> None:
    code, out = _run(["import-good"])
    assert code == 2 and "error" in out
