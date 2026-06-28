#!/usr/bin/env python
"""Construit le sidecar moteur **autonome** (PyInstaller onefile) pour Tauri externalBin.

Sortie : app/src-tauri/binaries/irminsul-sidecar-<triple>.exe — bundle l'interpréteur
Python + la stdlib + le moteur (account/account_ipc/sidecar). **Python n'est PAS requis
chez l'utilisateur final.** Le nom inclut le triple cible (arch Windows).

Usage : python tools/build_sidecar.py [--triple x86_64-pc-windows-msvc]
Pré-requis : pip install pyinstaller (dans le venv de build).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def host_triple() -> str:
    try:
        out = subprocess.run(["rustc", "-Vv"], capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            if line.startswith("host:"):
                return line.split(":", 1)[1].strip()
    except Exception:  # noqa: BLE001
        pass
    return "x86_64-pc-windows-msvc"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--triple", default="")
    args = ap.parse_args()
    triple = args.triple or host_triple()
    name = f"irminsul-sidecar-{triple}"
    out_dir = ROOT / "app" / "src-tauri" / "binaries"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = ROOT / ".irminsul" / "pyi"
    # Données de mécaniques embarquées dans l'exe (voyagent avec le moteur) :
    # registre des mécaniques + stats de base perso (versionnées, sourcées).
    mechanics_dir = ROOT / "data" / "mechanics"
    add_data_args: list[str] = []
    for fname in ("source-registry.json", "character-basestats.json"):
        f = mechanics_dir / fname
        if not f.exists():
            print(f"[build_sidecar] ERREUR: donnée requise absente: {f}")
            return 1
        add_data_args += ["--add-data", f"{f}{os.pathsep}data/mechanics"]
    cmd = [
        sys.executable, "-m", "PyInstaller", "--onefile", "--clean", "--noconfirm",
        "--name", name,
        "--paths", str(ROOT / "src"),
        *add_data_args,
        "--distpath", str(out_dir),
        "--workpath", str(work),
        "--specpath", str(work),
        str(ROOT / "tools" / "sidecar" / "sidecar_main.py"),
    ]
    print("[build_sidecar]", " ".join(cmd))
    result = subprocess.run(cmd)
    exe = out_dir / f"{name}.exe"
    if result.returncode == 0 and exe.exists():
        print(f"[build_sidecar] OK -> {exe} ({exe.stat().st_size} octets)")
        return 0
    print("[build_sidecar] ÉCHEC")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
