#!/usr/bin/env python
"""Extrait les stats de base des ARMES depuis genshin-db (gitignoré) vers le fichier
**committé** `data/mechanics/weapon-basestats.json`.

Source : `data/sources/genshin-db/src/data/{curve,stats}/weapons.json`.
Provenance REPRODUCTIBLE : commit + date du commit (pas date.today()).
Aucune valeur inventée (cf. weaponstats.extract_weapons_from_genshin_db).

Usage : python tools/extract_weapon_basestats.py [--source data/sources/genshin-db]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from irminsul.weaponstats import extract_weapons_from_genshin_db  # noqa: E402


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
    ap.add_argument("--out", default=str(ROOT / "data" / "mechanics" / "weapon-basestats.json"))
    args = ap.parse_args()

    source = Path(args.source)
    if not (source / "src" / "data" / "stats" / "weapons.json").exists():
        print(f"[extract_weapon_basestats] source introuvable: {source}", file=sys.stderr)
        return 1

    commit = _git(["rev-parse", "HEAD"], source)
    commit_date = _git(["show", "-s", "--format=%cI", "HEAD"], source)
    remote = _git(["remote", "get-url", "origin"], source) or "https://github.com/theBowja/genshin-db"

    extracted_at = commit_date[:10] if commit_date else ""
    # Durcissement (revue R3) : hash SHA256 des fichiers source + contrôle de PROPRETÉ du
    # checkout. 'reproducible' n'est vrai que si commit connu ET checkout propre (sinon la
    # sortie ne peut pas être reconstruite à partir du seul commit).
    src_rel = ["src/data/curve/weapons.json", "src/data/stats/weapons.json"]
    file_sha256 = {rel: hashlib.sha256((source / rel).read_bytes()).hexdigest() for rel in src_rel}
    porcelain = _git(["status", "--porcelain", "--", *src_rel], source)
    source_dirty = bool(porcelain)
    reproducible = bool(commit and commit_date) and not source_dirty
    if not reproducible:
        print("[extract_weapon_basestats] AVERTISSEMENT : provenance NON reproductible "
              f"(commit={'ok' if commit else 'absent'}, checkout {'sale' if source_dirty else 'propre'}) "
              "→ confiance abaissée.", file=sys.stderr)

    provenance = {
        "source": "genshin-db",
        "source_repo": "theBowja/genshin-db",
        "source_url": remote.replace(".git", ""),
        "source_commit": commit,
        "source_commit_date": commit_date,
        "extracted_from": src_rel,
        "source_file_sha256": file_sha256,
        "source_dirty": source_dirty,
        "extracted_at": extracted_at,
        "reproducible": reproducible,
        "confidence": "high" if reproducible else "medium",
    }

    payload = extract_weapons_from_genshin_db(source, provenance)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[extract_weapon_basestats] OK -> {out} "
          f"({payload['provenance']['weapon_count']} armes, commit {commit[:8]}, "
          f"{out.stat().st_size} octets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
