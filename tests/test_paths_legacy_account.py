"""Résolution du dossier de compte, y compris l'ancien emplacement desktop.

Régression réelle : d'anciennes versions desktop écrivaient le compte sous
`<data_dir>/data/account` (un niveau `data/` en trop). Après mise à jour, l'app
lisait `<data_dir>/account` — vide — et affichait « aucun scan » alors que le
compte du joueur existait bel et bien. Ces tests verrouillent le repli.
"""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def paths(monkeypatch, tmp_path):
    """Module `paths` avec IRMINSUL_DATA_DIR pointant sur un tmp isolé."""
    monkeypatch.setenv("IRMINSUL_DATA_DIR", str(tmp_path))
    module = importlib.import_module("irminsul.paths")
    return module, tmp_path


def test_account_dir_utilise_emplacement_canonique(paths):
    """Cas nominal : `<data_dir>/account` est créé et utilisé."""
    module, root = paths
    resolved = module.account_dir()
    assert resolved == root / "account"
    assert resolved.is_dir()


def test_account_dir_reprend_lancien_emplacement(paths):
    """Si SEUL l'ancien `<data_dir>/data/account` existe, on le lit."""
    module, root = paths
    legacy = root / "data" / "account" / "current"
    legacy.mkdir(parents=True)
    (legacy / "characters.json").write_text("[]", encoding="utf-8")

    resolved = module.account_dir()

    assert resolved == root / "data" / "account", (
        "un compte importé par une ancienne version doit rester visible"
    )
    assert (resolved / "current" / "characters.json").exists()


def test_canonique_prioritaire_sur_lancien(paths):
    """Si les deux existent, le canonique gagne (pas de retour en arrière)."""
    module, root = paths
    (root / "account").mkdir(parents=True)
    (root / "data" / "account").mkdir(parents=True)

    assert module.account_dir() == root / "account"


def test_aucun_compte_ne_cree_pas_lancien_chemin(paths):
    """Sans données, on crée le canonique — jamais le legacy."""
    module, root = paths
    resolved = module.account_dir()

    assert resolved == root / "account"
    assert not (root / "data" / "account").exists()
