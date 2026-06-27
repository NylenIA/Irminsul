"""Tests du moteur de calcul rapide (déterministe) et du registre des mécaniques."""

from __future__ import annotations

import pytest

from irminsul import quickcalc
from irminsul.account_ipc import dispatch


def test_registry_integrity() -> None:
    reg = quickcalc.load_registry()
    assert reg["schema"] >= 1 and reg["version"]
    assert reg["mechanics"], "registre non vide"
    for m in reg["mechanics"]:
        for key in ("id", "applies_to_versions", "rule", "sources", "code",
                    "tests", "verified_at", "status", "confidence"):
            assert key in m, f"{m.get('id')} manque '{key}'"
        assert m["status"] in quickcalc.VALID_STATUS
        assert m["sources"] and all("name" in s and "type" in s for s in m["sources"])


def test_quickcalc_golden_no_reaction() -> None:
    # Golden = calcul manuel indépendant :
    # base 2.0*2000=4000 ; ×(1+0.5)=6000 ; DefMult 190/390=0.487179 ; ResMult 0.9
    # non_crit=2630.77 ; expected=×(1+0.5*1.0)=3946.15 ; crit=×2=5261.54
    p = quickcalc.quickcalc_payload({
        "scaling": 2.0, "stat": 2000, "crit_rate": 0.5, "crit_damage": 1.0,
        "damage_bonus": 0.5,
    })
    r = p["result"]
    assert r["non_crit"] == pytest.approx(2630.77, abs=1.0)
    assert r["expected"] == pytest.approx(3946.15, abs=1.0)
    assert r["crit"] == pytest.approx(5261.54, abs=1.0)
    assert "outgoing_damage" in p["mechanics_used"]


def test_quickcalc_amplifying_doubles() -> None:
    base = quickcalc.quickcalc_payload({"scaling": 2.0, "stat": 2000})["result"]["expected"]
    vape = quickcalc.quickcalc_payload({
        "scaling": 2.0, "stat": 2000, "reaction": "forward-vaporize", "em": 0,
    })
    assert vape["result"]["expected"] == pytest.approx(base * 2.0, rel=1e-6)
    assert vape["amplifying"]["amplifying_multiplier"] == pytest.approx(2.0, rel=1e-6)
    assert "amplifying_reaction" in vape["mechanics_used"]


def test_quickcalc_requires_inputs() -> None:
    with pytest.raises(ValueError):
        quickcalc.quickcalc_payload({"scaling": 1.0})  # 'stat' manquant


def test_dispatch_mechanics_and_quickcalc() -> None:
    assert dispatch("mechanics")["status"] == "ok"
    out = dispatch("quick-calc", {"scaling": 1.5, "stat": 1800})
    assert out["status"] == "ok" and out["result"]["expected"] > 0
    assert out["registry_version"]


def test_determinism() -> None:
    a = quickcalc.quickcalc_payload({"scaling": 3.1, "stat": 2222, "crit_rate": 0.7,
                                     "crit_damage": 1.5, "damage_bonus": 0.466})
    b = quickcalc.quickcalc_payload({"scaling": 3.1, "stat": 2222, "crit_rate": 0.7,
                                     "crit_damage": 1.5, "damage_bonus": 0.466})
    assert a["result"] == b["result"]  # déterministe
