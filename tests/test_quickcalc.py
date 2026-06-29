"""Tests du moteur de calcul rapide (déterministe) et du registre des mécaniques."""

from __future__ import annotations

import pytest

from irminsul import quickcalc
from irminsul.account_ipc import dispatch
from irminsul.reaction import additive_reaction


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


def test_additive_base_bonus_golden() -> None:
    # Golden indépendant : coef × 1446.85 × (1 + 5·EM/(EM+1200)).
    # Aggravation EM0 : 1.15×1446.85 = 1663.88 ; Propagation : 1.25×1446.85 = 1808.56.
    assert additive_reaction(reaction="aggravate").base_bonus_damage == pytest.approx(1663.88, abs=1.0)
    assert additive_reaction(reaction="spread").base_bonus_damage == pytest.approx(1808.56, abs=1.0)
    # EM 200 : facteur (1 + 1000/1400) = 1.7143.
    assert additive_reaction(reaction="aggravate", elemental_mastery=200).base_bonus_damage == pytest.approx(
        1663.88 * 1.7143, rel=1e-3
    )


def test_additive_monotonic_in_em() -> None:
    lo = additive_reaction(reaction="spread", elemental_mastery=0).base_bonus_damage
    hi = additive_reaction(reaction="spread", elemental_mastery=300).base_bonus_damage
    assert hi > lo  # propriété : plus d'EM ⇒ plus de bonus


def test_quickcalc_additive_adds_to_base() -> None:
    no = quickcalc.quickcalc_payload({"scaling": 2.0, "stat": 2000})["result"]["expected"]
    agg = quickcalc.quickcalc_payload({"scaling": 2.0, "stat": 2000, "reaction": "aggravate", "em": 100})
    assert agg["additive"] is not None
    assert "additive_reaction" in agg["mechanics_used"]
    assert agg["result"]["expected"] > no  # le bonus additif augmente les dégâts


def test_quickcalc_transformative_block() -> None:
    out = quickcalc.quickcalc_payload({"scaling": 0.0, "stat": 0.0, "reaction": "overloaded"})
    assert out["transformative"] is not None
    # Golden : 2.0 × 1446.85 × (1+0) × ResMult(0.1)=0.9 = 2604.33.
    assert out["transformative"]["damage"] == pytest.approx(2604.33, abs=1.0)
    assert "transformative_reaction" in out["mechanics_used"]


def test_mechanics_detail_carries_source_and_confidence() -> None:
    out = quickcalc.quickcalc_payload({"scaling": 1.0, "stat": 1000, "reaction": "forward-vaporize"})
    ids = {m["id"] for m in out["mechanics_detail"]}
    assert {"outgoing_damage", "amplifying_reaction"} <= ids
    for m in out["mechanics_detail"]:
        assert m["status"] in quickcalc.VALID_STATUS and m["sources"] and "confidence" in m


def test_registry_flags_uncertain_lunar_as_unknown() -> None:
    reg = quickcalc.load_registry()
    ids = {m["id"]: m for m in reg["mechanics"]}
    assert "additive_reaction" in ids and ids["additive_reaction"]["status"] == "verified"
    assert "lunar_reactions" in ids and ids["lunar_reactions"]["status"] == "unknown"  # incertitude signalée


def test_unknown_reaction_rejected() -> None:
    with pytest.raises(ValueError):
        quickcalc.quickcalc_payload({"scaling": 1.0, "stat": 1000, "reaction": "lunar-charged"})


def test_determinism() -> None:
    a = quickcalc.quickcalc_payload({"scaling": 3.1, "stat": 2222, "crit_rate": 0.7,
                                     "crit_damage": 1.5, "damage_bonus": 0.466})
    b = quickcalc.quickcalc_payload({"scaling": 3.1, "stat": 2222, "crit_rate": 0.7,
                                     "crit_damage": 1.5, "damage_bonus": 0.466})
    assert a["result"] == b["result"]  # déterministe
