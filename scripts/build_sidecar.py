#!/usr/bin/env python3
"""Build REPRODUCTIBLE du sidecar moteur (PyInstaller onefile).

- Point d'entrée unique : src/irminsul/sidecar.py (dispatcher canonique).
- Génère src/irminsul/_buildinfo.py (commit, date, python) figé dans le binaire.
- Datas explicites : data/mechanics/*.json (basestats les résout via sys._MEIPASS).
- Sortie : app/src-tauri/binaries/irminsul-sidecar-x86_64-pc-windows-msvc.exe
- Écrit le SHA-256 dans .irminsul/proof/sidecar-build.json (preuve horodatée).

Usage : .venv/Scripts/python.exe scripts/build_sidecar.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = "irminsul-sidecar-x86_64-pc-windows-msvc"
DIST = ROOT / "app" / "src-tauri" / "binaries"
ENTRY = ROOT / "scripts" / "sidecar_entry.py"  # wrapper top-level (imports relatifs du package)
DATAS = sorted((ROOT / "data" / "mechanics").glob("*.json"))


def main() -> int:
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
        cwd=ROOT, check=False,
    ).stdout.strip() or "unknown"
    built_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    (ROOT / "src" / "irminsul" / "_buildinfo.py").write_text(
        f'"""Généré par scripts/build_sidecar.py — NE PAS éditer."""\n'
        f'GIT_COMMIT = "{commit}"\nBUILT_AT = "{built_at}"\nPYTHON = "{sys.version.split()[0]}"\n',
        encoding="utf-8",
    )

    args = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--clean",
        "--name", NAME, "--distpath", str(DIST),
        "--workpath", str(ROOT / ".irminsul" / "pyi" / "work"),
        "--specpath", str(ROOT / ".irminsul" / "pyi"),
        "--paths", str(ROOT / "src"),
        "--collect-submodules", "irminsul",  # imports paresseux du dispatcher tous embarqués
        "--console",  # stdio : le protocole EXIGE stdin/stdout (fenêtre cachée par l'appelant)
    ]
    for d in DATAS:
        args += ["--add-data", f"{d};data/mechanics"]
    args.append(str(ENTRY))
    print(f"[build_sidecar] commit={commit} datas={len(DATAS)}")
    r = subprocess.run(args, cwd=ROOT)
    if r.returncode != 0:
        return r.returncode

    exe = DIST / f"{NAME}.exe"
    h = hashlib.sha256(exe.read_bytes()).hexdigest()
    proof = {"binary": str(exe.relative_to(ROOT)), "sha256": h, "git_commit": commit,
             "built_at": built_at, "size_bytes": exe.stat().st_size}
    out = ROOT / ".irminsul" / "proof" / "sidecar-build.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(f"[build_sidecar] OK sha256={h[:16]}… size={proof['size_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
