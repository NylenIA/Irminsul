from __future__ import annotations

import json
import os
import platform
import re
import shutil
import stat
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "tools" / "bin"
API = "https://api.github.com/repos/genshinsim/gcsim/releases/latest"


def asset_score(name: str) -> int:
    lower = name.lower()
    system = platform.system().lower()
    machine = platform.machine().lower()
    score = 0
    if system in lower:
        score += 10
    if system == "windows" and ("win" in lower or lower.endswith(".exe")):
        score += 8
    if system == "linux" and "linux" in lower:
        score += 8
    if system == "darwin" and any(token in lower for token in ("darwin", "mac", "osx")):
        score += 8
    if machine in {"amd64", "x86_64"} and any(token in lower for token in ("amd64", "x86_64", "x64")):
        score += 5
    if machine in {"arm64", "aarch64"} and any(token in lower for token in ("arm64", "aarch64")):
        score += 5
    if "gcsim" in lower:
        score += 4
    if lower.endswith((".zip", ".tar.gz", ".tgz", ".exe")):
        score += 2
    return score


def main() -> int:
    BIN.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(API, headers={"User-Agent": "IrminsulAI/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            release = json.load(response)
    except Exception as exc:  # noqa: BLE001
        print(f"Impossible de lire la dernière release gcsim: {exc}")
        return 1

    assets = release.get("assets", [])
    ranked = sorted(assets, key=lambda a: asset_score(a.get("name", "")), reverse=True)
    if not ranked or asset_score(ranked[0].get("name", "")) < 10:
        print("Aucun binaire gcsim compatible détecté automatiquement.")
        print("Télécharge-le manuellement depuis les releases gcsim dans tools/bin/.")
        return 1

    asset = ranked[0]
    name = asset["name"]
    url = asset["browser_download_url"]
    archive = BIN / name
    print(f"Téléchargement de {name} ({release.get('tag_name', 'latest')})")
    urllib.request.urlretrieve(url, archive)

    target_name = "gcsim.exe" if os.name == "nt" else "gcsim"
    target = BIN / target_name
    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive) as zf:
            members = [m for m in zf.namelist() if re.search(r"gcsim(?:\.exe)?$", m, re.I)]
            if not members:
                print("Archive téléchargée mais exécutable introuvable.")
                return 1
            with zf.open(members[0]) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
        archive.unlink(missing_ok=True)
    elif archive.suffix.lower() == ".exe":
        archive.replace(target)
    else:
        print(f"Format {archive.suffix} non extrait automatiquement.")
        return 1

    if os.name != "nt":
        target.chmod(target.stat().st_mode | stat.S_IEXEC)
    print(f"gcsim installé : {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
