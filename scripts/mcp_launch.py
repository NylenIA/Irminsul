from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

if not PYTHON.exists():
    print("Irminsul AI n'est pas installé. Lance scripts/bootstrap.ps1.", file=sys.stderr)
    raise SystemExit(2)

os.environ.setdefault("IRMINSUL_PROJECT_ROOT", str(ROOT))

# Sous Windows, os.execv casse l'héritage des pipes stdio : le client MCP perd
# la connexion au serveur. On lance donc un sous-processus qui hérite des mêmes
# flux stdin/stdout/stderr (la liaison JSON-RPC du client passe au serveur).
# Sur POSIX, os.execv reste le choix idiomatique (zéro processus supplémentaire).
if os.name == "nt":
    completed = subprocess.run([str(PYTHON), "-m", "irminsul.mcp_server"])
    raise SystemExit(completed.returncode)
os.execv(str(PYTHON), [str(PYTHON), "-m", "irminsul.mcp_server"])
