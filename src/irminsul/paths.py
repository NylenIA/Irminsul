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
