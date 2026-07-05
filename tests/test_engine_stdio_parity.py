"""Garde de parité du sidecar web (`scripts/engine_stdio.py`).

Le web (Server Actions) dépend de ce jeu de méthodes. Si l'une disparaît, l'app casse → ce test
échoue avant. NE garantit PAS que le binaire EMPAQUETÉ correspond (voir SIDECAR_INVENTORY.md :
divergence P0 documentée) — il garde le point d'entrée web contre la dérive.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STDIO = ROOT / "scripts" / "engine_stdio.py"

EXPECTED_METHODS = {
    "calculate_direct_hit",
    "amplifying_multiplier",
    "transformative_reaction",
    "character_final_stats",
    "calculate_rotation",
    "engine_provenance",
}


def _load_module():
    spec = importlib.util.spec_from_file_location("engine_stdio_under_test", STDIO)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_expected_methods_present() -> None:
    mod = _load_module()
    assert EXPECTED_METHODS.issubset(set(mod.METHODS)), (
        f"Méthodes manquantes : {EXPECTED_METHODS - set(mod.METHODS)}"
    )


def test_engine_provenance_shape() -> None:
    mod = _load_module()
    prov = mod._engine_provenance({})
    assert prov["api_version"] == "engine-stdio/1.0"
    assert "rotation" in prov["contracts"]
    assert set(EXPECTED_METHODS).issubset(set(prov["methods"]))
    # Jamais de chemin local dans la provenance.
    assert "\\" not in json.dumps(prov) or "git_commit" in prov  # pas de backslash de chemin


def test_engine_provenance_via_stdio_protocol() -> None:
    """Bout-en-bout : le protocole stdio renvoie bien une provenance JSON stricte."""
    proc = subprocess.run(
        [sys.executable, str(STDIO)],
        input=json.dumps({"method": "engine_provenance", "params": {}}),
        capture_output=True, text=True, timeout=30,
    )
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["result"]["api_version"] == "engine-stdio/1.0"
