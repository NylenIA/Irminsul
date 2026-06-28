#!/usr/bin/env python
"""Exécute une commande en gardant la sortie COMPLÈTE dans .irminsul/logs/ et en
ne renvoyant au modèle qu'un résumé compact — SANS jamais masquer le code de
sortie réel ni les erreurs (cf. MASTER_SPEC §5.3).

Usage : python scripts/run_logged.py [--tail N] [--label nom] -- <commande...>
Sortie : code de sortie réel propagé ; stdout = résumé + chemin du log complet.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / ".irminsul" / "logs"
ERROR_RE = re.compile(r"\b(error|erreur|failed|échec|traceback|exception|FAILED|E\s)\b", re.I)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail", type=int, default=15)
    ap.add_argument("--label", default="cmd")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.rest[1:] if args.rest and args.rest[0] == "--" else args.rest
    if not cmd:
        print("Aucune commande fournie (… -- <commande>).", file=sys.stderr)
        return 2

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", args.label)[:40]
    log_path = LOG_DIR / f"{ts}-{safe}.log"

    # Résout un exécutable fourni en chemin relatif au dépôt (ex. .venv/Scripts/python.exe).
    candidate = ROOT / cmd[0]
    if candidate.exists():
        cmd = [str(candidate), *cmd[1:]]

    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)  # noqa: S603
    full = (proc.stdout or "") + (("\n--- STDERR ---\n" + proc.stderr) if proc.stderr else "")
    log_path.write_text(full, encoding="utf-8", errors="replace")

    lines = full.splitlines()
    error_lines = [ln for ln in lines if ERROR_RE.search(ln)]
    # Dédoublonne les erreurs en gardant l'ordre.
    seen: set[str] = set()
    uniq_err = [e for e in error_lines if not (e in seen or seen.add(e))][:10]

    print(f"[run_logged] exit={proc.returncode} label={safe} lines={len(lines)} log={log_path}")
    if uniq_err:
        print(f"[run_logged] {len(error_lines)} ligne(s) d'erreur (uniques: {len(uniq_err)}):")
        for e in uniq_err:
            print("  " + e.strip()[:200])
    if args.tail > 0 and lines:
        print(f"[run_logged] tail -{args.tail}:")
        for ln in lines[-args.tail:]:
            print("  " + ln[:200])
    # Propager le VRAI code de sortie (jamais remplacé par un pipe).
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
