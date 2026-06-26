"""Tests de l'optimiseur d'équipes — et verrou de non-régression méta.

Encode durablement la correction : sur Mavuika Melt, quand Citlali couvre déjà le
shred de RES, **Iansan** (offensif) dépasse **Xilonen** (RES shred redondant).
Si une future modif réintroduit l'erreur « Xilonen > Iansan ici », ce test casse.
"""

from __future__ import annotations

from irminsul.team_optimizer import (
    load_profiles,
    optimize,
    team_damage_index,
)


def test_profiles_load_seed() -> None:
    carries, supports = load_profiles()
    assert "Mavuika" in carries
    assert {"Citlali", "Iansan", "Xilonen", "Bennett"} <= set(supports)


def test_iansan_beats_xilonen_in_mavuika_citlali_team() -> None:
    """LE verrou : Citlali + Iansan + Bennett > Citlali + Xilonen + Bennett."""
    carries, supports = load_profiles()
    mav = carries["Mavuika"]
    base = [supports["Citlali"], supports["Bennett"]]
    iansan = team_damage_index(mav, base + [supports["Iansan"]], reaction="forward-melt")
    xilonen = team_damage_index(mav, base + [supports["Xilonen"]], reaction="forward-melt")
    assert iansan["index"] > xilonen["index"], (
        f"Iansan ({iansan['index']}) doit dépasser Xilonen ({xilonen['index']}) "
        "dans la team Citlali de Mavuika (RES déjà shred par Citlali)."
    )


def test_best_mavuika_melt_team_is_citlali_iansan_bennett() -> None:
    result = optimize("Mavuika", reaction="forward-melt", top=3)
    assert result["top"], "Au moins une équipe valide attendue."
    best = result["top"][0]
    assert best["team"][0] == "Mavuika"
    assert set(best["supports"]) == {"Citlali", "Iansan", "Bennett"}


def test_melt_requires_cryo_enabler() -> None:
    # Sans support cryo activateur, aucune équipe melt n'est valide.
    result = optimize("Mavuika", reaction="forward-melt", pool=["Iansan", "Xilonen", "Bennett"])
    assert result["candidates_evaluated"] == 0


def test_natlan_requirement_enforced() -> None:
    # Mavuika exige >= 2 Natlan (elle-même + 1). Bennett/Rosaria/Diona ne sont pas Natlan.
    result = optimize("Mavuika", reaction="forward-melt", pool=["Bennett", "Rosaria", "Diona"])
    assert result["candidates_evaluated"] == 0


def test_furina_excluded_from_melt_but_usable_in_vaporize() -> None:
    melt = optimize("Mavuika", reaction="forward-melt", top=10)
    assert all("Furina" not in t["supports"] for t in melt["top"])  # hydro gêne le melt
    vape = optimize("Mavuika", reaction="forward-vaporize", top=10)
    assert any("Furina" in t["supports"] for t in vape["top"])  # Furina = activateur vape


def test_unknown_carry_raises() -> None:
    import pytest
    with pytest.raises(KeyError):
        optimize("PersonnageInexistant")
