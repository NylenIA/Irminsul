$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$LogDir = Join-Path $Root "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir "scheduled-update.log"
"[$(Get-Date -Format o)] update start" | Out-File -Append -Encoding utf8 $Log
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Environnement .venv introuvable" }
try {
  & $Python -m irminsul.cli update *>> $Log
  "[$(Get-Date -Format o)] update success" | Out-File -Append -Encoding utf8 $Log
} catch {
  "[$(Get-Date -Format o)] update failed: $_" | Out-File -Append -Encoding utf8 $Log
  throw
}
