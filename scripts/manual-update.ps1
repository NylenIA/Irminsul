param([switch]$SkipGcsim)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  throw "Irminsul AI n'est pas encore installé. Lance INSTALLER_IRMINSUL.bat."
}

if (-not $SkipGcsim) {
  & $Python tools/install_gcsim.py
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "La mise à jour de gcsim a échoué, mais les sources vont quand même être actualisées."
  }
}

& $Python -m irminsul.cli update
if ($LASTEXITCODE -ne 0) { throw "Échec de la mise à jour de la base Irminsul." }
& $Python -m irminsul.cli status
Write-Host "Mise à jour terminée."
