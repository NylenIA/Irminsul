#!/usr/bin/env bash
# Validation globale du projet Irminsul AI : lint Ruff + tests pytest + doctor.
# Usage : bash scripts/validate.sh
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONPATH=src
PY=".venv/Scripts/python.exe"
[ -x "$PY" ] || PY="python"

status=0
echo "== Ruff =="
"$PY" -m ruff check src tests || status=1
echo "== Pytest =="
"$PY" -m pytest -q || status=1
echo "== Doctor (informatif) =="
"$PY" -m irminsul.cli doctor || true

if [ "$status" -eq 0 ]; then
  echo "✅ Validation OK (lint + tests)."
else
  echo "❌ Validation en échec : voir ci-dessus."
fi
exit "$status"
