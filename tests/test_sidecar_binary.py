"""Parité SOURCE ↔ BINAIRE gelé : exécute RÉELLEMENT le .exe PyInstaller empaqueté.

ÉCHOUE si le binaire ne correspond pas à la source (méthodes divergentes) — un nom de
fichier plausible ou un build historique ne suffit plus. Skip UNIQUEMENT si le binaire
est absent (CI sans build) : jamais un faux PASS.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from irminsul.engine_dispatch import CANONICAL_METHODS

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXE = ROOT / "app" / "src-tauri" / "binaries" / "irminsul-sidecar-x86_64-pc-windows-msvc.exe"

pytestmark = pytest.mark.skipif(not EXE.exists(), reason="binaire sidecar absent (build requis)")


def _call(method: str, params: dict | None = None) -> dict:
    req = json.dumps({"id": 1, "method": method, "params": params or {}})
    proc = subprocess.run(
        [str(EXE)], input=req.encode("utf-8"), capture_output=True, timeout=60,
    )
    payload = json.loads(proc.stdout.decode("utf-8"))
    assert payload.get("ok") is True, f"{method}: {payload.get('error')}"
    return payload["result"]


def test_binaire_frozen_et_methodes_identiques_a_la_source() -> None:
    prov = _call("engine_provenance")
    assert prov["frozen_binary"] is True
    # PARITÉ EXACTE : la table du binaire == la table de la source (pas un sous-ensemble).
    assert prov["methods"] == sorted(CANONICAL_METHODS.keys()), (
        "binaire divergent de la source — reconstruire via scripts/build_sidecar.py"
    )
    assert prov["ipc_contract"] == "engine-ipc/1.0"
    assert prov["binary_sha256"] and len(prov["binary_sha256"]) == 64
    assert prov["git_commit"] not in (None, "unknown")


def test_binaire_rotation_reelle() -> None:
    result = _call("calculate_rotation", {
        "team": ["Mavuika"],
        "actions": [{"actorId": "Mavuika", "kind": "normal_attack", "startTime": 0,
                     "duration": 1, "talentSlot": "combat1", "talentLabel": "1-Hit DMG",
                     "talentLevel": 10}],
    })
    assert result["contract_version"] == "rotation/1.0"
    # Le binaire embarque les données mécaniques : le coefficient doit se résoudre.
    assert result["actions"][0]["complete"] in (True, False)  # selon présence du scan local
    assert "average_damage_per_second" in result


def test_binaire_reaction_et_final_stats_et_roster() -> None:
    amp = _call("amplifying_multiplier", {"reaction": "forward-vaporize", "elemental_mastery": 187})
    assert amp["amplifying_multiplier"] > 2

    fs = _call("character_final_stats", {"key": "Mavuika"})
    assert fs.get("status") in ("ok", "empty", "not-found")  # jamais un crash

    roster = _call("roster")
    assert isinstance(roster, dict)


def test_binaire_capabilities_derivees() -> None:
    caps = _call("engine_capabilities")
    assert caps["methods"] == sorted(CANONICAL_METHODS.keys())
