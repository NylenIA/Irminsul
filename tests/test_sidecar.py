"""Tests du protocole sidecar (côté Python). Les cas runtime (sidecar absent,
timeout, processus tué, pas de Python) sont couverts côté Rust."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from irminsul import sidecar


def _call(obj: object) -> dict:
    raw = obj if isinstance(obj, (bytes, bytearray)) else json.dumps(obj).encode("utf-8")
    return json.loads(sidecar.handle(raw).decode("utf-8"))


@pytest.fixture()
def account_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "data root"  # espace dans le chemin
    root.mkdir()
    monkeypatch.setenv("IRMINSUL_PROJECT_ROOT", str(root))
    return root


def _good(path: Path, n_chars: int = 1) -> Path:
    chars = [{"key": f"C{i}", "level": 90, "constellation": 0, "ascension": 6,
              "talent": {"auto": 1, "skill": 6, "burst": 6}} for i in range(n_chars)]
    path.write_text(json.dumps({
        "format": "GOOD", "version": 3, "source": "Inventory_Kamera",
        "characters": chars,
        "weapons": [{"key": "FavoniusSword", "level": 90, "ascension": 6,
                     "refinement": 1, "location": "C0", "lock": True, "id": 0}],
        "artifacts": [], "materials": {"Mora": 1000},
    }), encoding="utf-8")
    return path


def test_valid_request_empty_account(account_root: Path) -> None:
    out = _call({"id": "r1", "method": "profile"})
    assert out["id"] == "r1" and out["ok"] is True
    assert out["result"]["status"] == "empty"  # jamais de donnée inventée


def test_import_then_roster_keeps_provenance(tmp_path: Path, account_root: Path) -> None:
    good = _good(tmp_path / "acc_GOOD.json")
    imp = _call({"id": 1, "method": "import-good", "params": {"path": str(good)}})
    assert imp["ok"] is True
    assert "validation" in imp["result"]["import"]  # anomalies conservées

    prof = _call({"id": 2, "method": "profile"})
    assert prof["result"]["profile"]["sha256"]  # provenance
    rost = _call({"id": 3, "method": "roster"})
    assert rost["result"]["roster"]["characters"][0]["key"] == "C0"


def test_invalid_json() -> None:
    out = _call(b"{ pas du json")
    assert out["ok"] is False and out["error"]["type"] == "invalid_json"


def test_unknown_method() -> None:
    out = _call({"id": 9, "method": "explode"})
    assert out["ok"] is False and out["error"]["type"] == "bad_request"
    assert out["id"] == 9


def test_missing_method() -> None:
    out = _call({"id": 9, "params": {}})
    assert out["ok"] is False and out["error"]["type"] == "bad_request"


def test_empty_request() -> None:
    out = _call(b"")
    assert out["ok"] is False and out["error"]["type"] == "bad_request"


def test_oversized_request_is_bounded() -> None:
    big = b'{"method":"profile","pad":"' + b"x" * (sidecar.MAX_INPUT + 10) + b'"}'
    out = _call(big)
    assert out["ok"] is False and "volumineuse" in out["error"]["message"]


def test_unicode_and_space_path(tmp_path: Path, account_root: Path) -> None:
    d = tmp_path / "dossier éspacé ☃"
    d.mkdir()
    good = _good(d / "acc_GOOD.json")
    out = _call({"id": "u", "method": "import-good", "params": {"path": str(good)}})
    assert out["ok"] is True and out["result"]["import"]["counts"]["characters"] == 1


def test_large_good_file(tmp_path: Path, account_root: Path) -> None:
    good = _good(tmp_path / "big_GOOD.json", n_chars=400)
    assert good.stat().st_size > 20_000
    out = _call({"id": "big", "method": "import-good", "params": {"path": str(good)}})
    assert out["ok"] is True and out["result"]["import"]["counts"]["characters"] == 400
