"""Validation de l'UID Enka — ces tests ne font AUCUNE requête réseau.

`fetch_showcase` valide le format de l'UID avant tout appel HTTP : un UID
invalide doit lever immédiatement une ValueError.
"""

import pytest

from irminsul.enka import fetch_showcase


@pytest.mark.parametrize(
    "bad_uid",
    [
        "",          # vide
        "123",       # trop court
        "1234567",   # 7 chiffres
        "12345678901",  # 11 chiffres
        "70000000a",    # caractère non numérique
        "abcdefgh",     # lettres
        " 700000000",   # espace parasite
    ],
)
def test_invalid_uid_rejected_without_network(bad_uid) -> None:
    with pytest.raises(ValueError, match="UID"):
        fetch_showcase(bad_uid)


@pytest.mark.parametrize("ok_uid", ["12345678", "700000000", "1234567890"])
def test_valid_uid_format_passes_validation(ok_uid, monkeypatch) -> None:
    """Un UID bien formé passe la validation. On coupe le réseau pour le prouver
    sans dépendre d'Enka : on remplace httpx.get par une sentinelle."""
    import irminsul.enka as enka

    class _Stop(RuntimeError):
        pass

    def _fake_get(*args, **kwargs):
        raise _Stop("réseau atteint — la validation d'UID a été franchie")

    # Pas de cache pour cet UID -> on doit atteindre l'appel réseau simulé.
    monkeypatch.setattr(enka.httpx, "get", _fake_get)
    with pytest.raises(_Stop):
        fetch_showcase(ok_uid, force=True)
