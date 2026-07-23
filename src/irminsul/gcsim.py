from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .paths import project_root

_NUM = r"[\d.,]+"
DPS_PATTERN = re.compile(
    rf"Average\s+(?P<damage>{_NUM})\s+damage\s+over\s+(?P<duration>{_NUM})\s+seconds,"
    rf"\s+resulting\s+in\s+(?P<dps>{_NUM})\s+dps",
    re.IGNORECASE,
)
# Repli si le format principal change : on récupère au moins le DPS moyen.
DPS_FALLBACK = re.compile(rf"(?P<dps>{_NUM})\s+dps", re.IGNORECASE)


def _to_float(value: str) -> float:
    return float(value.replace(",", ""))


def gcsim_path() -> Path:
    configured = os.getenv("IRMINSUL_GCSIM_PATH")
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else project_root() / path
    bin_dir = project_root() / "tools" / "bin"
    canonical = bin_dir / ("gcsim.exe" if os.name == "nt" else "gcsim")
    if canonical.exists():
        return canonical
    # Repli : accepte un binaire gcsim au nom non canonique
    # (ex. gcsim_windows_amd64.exe téléchargé manuellement depuis les releases).
    if bin_dir.exists():
        pattern = "gcsim*.exe" if os.name == "nt" else "gcsim*"
        candidates = sorted(
            p for p in bin_dir.glob(pattern)
            if p.is_file() and (os.name == "nt" or os.access(p, os.X_OK))
        )
        if candidates:
            return candidates[0]
    return canonical


def run_gcsim(config_path: str | Path, open_viewer: bool = False) -> dict[str, Any]:
    executable = gcsim_path()
    config = Path(config_path)
    if not config.is_absolute():
        config = project_root() / config
    if not executable.exists():
        raise FileNotFoundError(
            f"gcsim introuvable à {executable}. Lance scripts/bootstrap.ps1 ou tools/install_gcsim.py."
        )
    if not config.exists():
        raise FileNotFoundError(f"Configuration gcsim introuvable : {config}")

    command = [str(executable), "-c", str(config)]
    if open_viewer:
        command.append("-s")
    completed = subprocess.run(
        command,
        cwd=project_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=600,
        check=False,
    )
    output = completed.stdout
    match = DPS_PATTERN.search(output)
    parsed = None
    if match:
        parsed = {key: _to_float(value) for key, value in match.groupdict().items()}
    else:
        fallback = DPS_FALLBACK.search(output)
        if fallback:
            parsed = {"dps": _to_float(fallback.group("dps")), "partial": True}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "command": command,
        "parsed": parsed,
        "output": output[-12000:],
    }


def run_gcsim_content(content: str) -> dict[str, Any]:
    """Simulation gcsim depuis un CONTENU de config (pas un chemin).

    Écrit un fichier temporaire, exécute le binaire local, renvoie le résultat
    de `run_gcsim` SANS la clé `command` (pas de chemin machine dans l'IPC).
    Erreurs explicites : config vide ou binaire absent — jamais de DPS inventé.
    """
    import tempfile

    if not content or not content.strip():
        raise ValueError("Configuration gcsim vide : fournis un script de simulation.")
    tmp = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8", prefix="irminsul-gcsim-"
    )
    try:
        tmp.write(content)
        tmp.close()
        result = run_gcsim(tmp.name)
        result.pop("command", None)
        return result
    finally:
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
