from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    configured = os.getenv("IRMINSUL_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "CLAUDE.md").exists():
            return candidate
    return current


def data_dir() -> Path:
    """Racine des données.

    Priorité à `IRMINSUL_DATA_DIR` (posée par l'app desktop : le sidecar gelé
    tourne hors du dépôt et doit lire/écrire le compte dans le dossier de
    données utilisateur, p.ex. %APPDATA%/com.nylenia.irminsul). À défaut
    (dev/CLI), on retombe sur `<repo>/data` comme avant.
    """
    configured = os.getenv("IRMINSUL_DATA_DIR")
    if configured:
        path = Path(configured).expanduser().resolve()
    else:
        path = project_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def sources_dir() -> Path:
    path = data_dir() / "sources"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> Path:
    path = data_dir() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "irminsul.db"


def account_dir() -> Path:
    """Racine des données de compte du joueur (jamais committée, cf. .gitignore).

    Emplacement CANONIQUE : `<data_dir>/account`.

    Repli HISTORIQUE : d'anciennes versions desktop écrivaient sous
    `<data_dir>/data/account` (un niveau `data/` en trop). Un compte importé
    avec ces versions devenait INVISIBLE après mise à jour. On lit l'ancien
    emplacement s'il est le seul à exister, plutôt que de perdre le compte.
    Miroir exact de `accountDir()` dans `apps/web/src/server/account.ts`.
    """
    canonical = data_dir() / "account"
    if not canonical.exists():
        legacy = data_dir() / "data" / "account"
        if legacy.exists():
            return legacy
    canonical.mkdir(parents=True, exist_ok=True)
    return canonical


def account_subdir(name: str) -> Path:
    """Sous-dossier de compte (raw, snapshots, current, reports, recommendations)."""
    path = account_dir() / name
    path.mkdir(parents=True, exist_ok=True)
    return path
