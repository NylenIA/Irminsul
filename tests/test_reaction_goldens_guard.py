"""Garde de parité réactions : les goldens committés doivent matcher le moteur actuel.

Si reaction.py évolue sans régénérer (scripts/gen-reaction-goldens.py), CE test casse.
"""
from __future__ import annotations

import json
import math
import pathlib

import pytest

from irminsul.reaction import amplifying_multiplier, transformative_reaction

GOLDENS = (
    pathlib.Path(__file__).resolve().parents[1]
    / "packages" / "engine-client" / "tests" / "reaction.goldens.json"
)


@pytest.mark.skipif(not GOLDENS.exists(), reason="goldens réactions absents")
def test_reaction_goldens_match_engine() -> None:
    payload = json.loads(GOLDENS.read_text(encoding="utf-8"))
    for case in payload["amplifying"]:
        result = amplifying_multiplier(**case["inputs"]).to_dict()
        for key, expected in case["expected"].items():
            if isinstance(expected, str):
                assert result[key] == expected
            else:
                assert math.isclose(result[key], expected, abs_tol=1e-12), (key, case)
    for case in payload["transformative"]:
        result = transformative_reaction(**case["inputs"]).to_dict()
        for key, expected in case["expected"].items():
            if isinstance(expected, str):
                assert result[key] == expected
            else:
                assert math.isclose(result[key], expected, abs_tol=1e-12), (key, case)
