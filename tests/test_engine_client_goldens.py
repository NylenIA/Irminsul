"""Garde de parité (finding High de l'audit Codex de l'ADR).

Les goldens committés de `packages/engine-client` doivent correspondre EXACTEMENT au
moteur Python actuel. Si `calculate_direct_hit` évolue sans régénérer les goldens
(`python scripts/gen-engine-goldens.py`), CE test casse — le portage TypeScript ne peut
donc plus rester « vert » pendant que le moteur de référence dérive.
"""
from __future__ import annotations

import json
import math
import pathlib

import pytest

from irminsul.damage import calculate_direct_hit

GOLDENS = (
    pathlib.Path(__file__).resolve().parents[1]
    / "packages"
    / "engine-client"
    / "tests"
    / "direct-hit.goldens.json"
)


@pytest.mark.skipif(not GOLDENS.exists(), reason="goldens engine-client absents")
def test_goldens_match_current_python_engine() -> None:
    payload = json.loads(GOLDENS.read_text(encoding="utf-8"))
    cases = payload["cases"]
    assert cases, "aucun cas golden"
    for i, case in enumerate(cases):
        result = calculate_direct_hit(**case["inputs"]).to_dict()
        for key, expected in case["expected"].items():
            assert math.isclose(result[key], expected, rel_tol=0, abs_tol=1e-12), (
                f"cas {i}, champ {key}: moteur={result[key]!r} != golden={expected!r}. "
                "Le moteur a changé : régénérer via scripts/gen-engine-goldens.py "
                "et re-vérifier la parité TypeScript."
            )
