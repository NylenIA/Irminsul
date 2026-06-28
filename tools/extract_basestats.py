#!/usr/bin/env python
"""Extrait les stats de base des personnages depuis genshin-db (gitignoré) vers le
fichier **committé** `data/mechanics/character-basestats.json`.

Source : `data/sources/genshin-db/src/data/{curve,stats}/characters.json`.
Provenance : commit + date du checkout genshin-db (git), formule + confiance.
Aucune valeur inventée : on copie/convertit fidèlement (cf. basestats.extract_*).

Usage : python tools/extract_basestats.py [--source data/sources/genshin-db]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from irminsul.basestats import extract_from_genshin_db  # noqa: E402


def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(ROOT / "data" / "sources" / "genshin-db"))
    ap.add_argument("--out", default=str(ROOT / "data" / "mechanics" / "character-basestats.json"))
    args = ap.parse_args()

    source = Path(args.source)
    if not (source / "src" / "data" / "stats" / "characters.json").exists():
        print(f"[extract_basestats] source introuvable: {source}", file=sys.stderr)
        return 1

    commit = _git(["rev-parse", "HEAD"], source)
    commit_date = _git(["show", "-s", "--format=%cI", "HEAD"], source)
    remote = _git(["remote", "get-url", "origin"], source) or "https://github.com/theBowja/genshin-db"

    provenance = {
        "source": "genshin-db",
        "source_repo": "theBowja/genshin-db",
        "source_url": remote.replace(".git", ""),
        "source_commit": commit,
        "source_commit_date": commit_date,
        "extracted_from": [
            "src/data/curve/characters.json",
            "src/data/stats/characters.json",
        ],
        "extracted_at": date.today().isoformat(),
    }

    payload = extract_from_genshin_db(source, provenance)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"[extract_basestats] OK -> {out} "
        f"({payload['provenance']['character_count']} persos, "
        f"commit {commit[:8]}, {out.stat().st_size} octets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
