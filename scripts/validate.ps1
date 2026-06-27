# Validation globale du projet Irminsul AI : lint Ruff + tests pytest + doctor.
# Usage : powershell -ExecutionPolicy Bypass -File scripts/validate.ps1
$ErrorActionPreference = "Continue"
Set-Location (Join-Path $PSScriptRoot "..")
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"; $env:PYTHONPATH = "src"
$py = ".venv/Scripts/python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$status = 0
Write-Host "== Ruff =="
& $py -m ruff check src tests; if ($LASTEXITCODE -ne 0) { $status = 1 }
Write-Host "== Pytest =="
& $py -m pytest -q; if ($LASTEXITCODE -ne 0) { $status = 1 }
Write-Host "== Doctor (informatif) =="
& $py -m irminsul.cli doctor

if ($status -eq 0) { Write-Host "OK Validation (lint + tests)." }
else { Write-Host "ECHEC Validation : voir ci-dessus." }
exit $status
