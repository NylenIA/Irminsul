"""Tests gcsim : gestion d'erreur déterministe + simulation réelle reproductible.

Le test d'intégration est automatiquement ignoré si le binaire gcsim n'est pas
installé : l'agent doit alors expliquer ce qui manque, pas inventer un résultat.
"""

from pathlib import Path

import pytest

from irminsul.gcsim import gcsim_path, run_gcsim

SMOKE = Path("simulations") / "smoke-test.txt"


def test_run_gcsim_reports_missing_binary(monkeypatch, tmp_path) -> None:
    """Sans binaire, run_gcsim lève une erreur claire au lieu d'inventer un DPS."""
    bogus = tmp_path / "no-gcsim.exe"
    monkeypatch.setenv("IRMINSUL_GCSIM_PATH", str(bogus))
    with pytest.raises(FileNotFoundError, match="gcsim"):
        run_gcsim(SMOKE)


def test_run_gcsim_reports_missing_config(monkeypatch) -> None:
    """Binaire présent mais config absente -> erreur explicite sur la config."""
    if not gcsim_path().exists():
        pytest.skip("binaire gcsim non installé")
    with pytest.raises(FileNotFoundError, match="[Cc]onfig"):
        run_gcsim("simulations/__inexistant__.txt")


@pytest.mark.integration
def test_run_gcsim_real_smoke() -> None:
    """Simulation réelle reproductible (Bennett seul). Ignorée sans binaire."""
    if not gcsim_path().exists():
        pytest.skip("binaire gcsim non installé")
    result = run_gcsim(SMOKE)
    assert result["ok"] is True, result["output"][-500:]
    assert result["parsed"] is not None
    assert result["parsed"]["dps"] > 0
    assert result["parsed"]["duration"] == pytest.approx(90.0, abs=1.0)
