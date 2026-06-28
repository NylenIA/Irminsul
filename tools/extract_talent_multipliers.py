#!/usr/bin/env python
"""Extrait les multiplicateurs de talents (valeurs par niveau + libellés) depuis
genshin-db (gitignoré) vers le fichier **committé** `data/mechanics/talent-multipliers.json`.

Sources : `src/data/stats/talents.json` (valeurs) + `src/data/English/talents/<perso>.json`
(libellés `attributes.labels`). Provenance REPRODUCTIBLE (commit + date du commit).
Aucune valeur inventée (cf. talentstats.extract_talents_from_genshin_db).

Usage : python tools/extract_talent_multipliers.py [--source data/sources/genshin-db]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from irminsul.talentstats import extract_talents_from_genshin_db  # noqa: E402


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
    ap.add_argument("--out", default=str(ROOT / "data" / "mechanics" / "talent-multipliers.json"))
    args = ap.parse_args()

    source = Path(args.source)
    if not (source / "src" / "data" / "stats" / "talents.json").exists():
        print(f"[extract_talent_multipliers] source introuvable: {source}", file=sys.stderr)
        return 1

    commit = _git(["rev-parse", "HEAD"], source)
    commit_date = _git(["show", "-s", "--format=%cI", "HEAD"], source)
    remote = _git(["remote", "get-url", "origin"], source) or "https://github.com/theBowja/genshin-db"

    extracted_at = commit_date[:10] if commit_date else ""
    reproducible = bool(commit and commit_date)
    if not reproducible:
        print("[extract_talent_multipliers] AVERTISSEMENT : source sans commit git → "
              "provenance non reproductible (confiance abaissée).", file=sys.stderr)

    provenance = {
        "source": "genshin-db",
        "source_repo": "theBowja/genshin-db",
        "source_url": remote.replace(".git", ""),
        "source_commit": commit,
        "source_commit_date": commit_date,
        "extracted_from": [
            "src/data/stats/talents.json",
            "src/data/English/talents/<perso>.json",
        ],
        "extracted_at": extracted_at,
        "reproducible": reproducible,
        "confidence": "high" if reproducible else "medium",
    }

    payload = extract_talents_from_genshin_db(source, provenance)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[extract_talent_multipliers] OK -> {out} "
          f"({payload['provenance']['character_count']} persos, "
          f"{payload['provenance']['skipped_count']} ignorés, commit {commit[:8]}, "
          f"{out.stat().st_size} octets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
