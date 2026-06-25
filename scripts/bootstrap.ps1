param(
  [switch]$NoSchedule,
  [switch]$SkipGcsim,
  [switch]$SkipSources,
  [switch]$SkipProfile
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Require-Command($Name, $Hint) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "$Name est requis. $Hint"
  }
}

function Optional-Command($Name, $Hint) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    Write-Warning "$Name introuvable. $Hint"
    return $false
  }
  return $true
}

# Indispensables au cœur Python.
Require-Command python "Installe Python 3.11 ou plus récent."
Require-Command git "Installe Git for Windows."
# Utiles mais non bloquants : on peut installer Irminsul avant Claude Code.
Optional-Command npm "Node.js LTS est conseillé (installation de Claude Code via npm)." | Out-Null
Optional-Command claude "Installe Claude Code avant de lancer START_IRMINSUL.bat." | Out-Null

$Version = & python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
if ([version]$Version -lt [version]"3.11") {
  throw "Python 3.11+ requis, version détectée: $Version"
}

# Tente uv ; bascule sur venv + pip si indisponible. $Py exécute ensuite tout dans l'env.
$UseUv = $false
python -c "import uv" 2>$null
if ($LASTEXITCODE -ne 0) {
  python -m pip install --user uv 2>$null
}
python -c "import uv" 2>$null
if ($LASTEXITCODE -eq 0) {
  python -m uv sync --all-extras
  if ($LASTEXITCODE -eq 0) { $UseUv = $true }
}

if (-not $UseUv) {
  Write-Warning "uv indisponible : repli sur venv + pip."
  if (-not (Test-Path ".venv")) { python -m venv .venv }
  $VenvPy = Join-Path $Root ".venv\Scripts\python.exe"
  & $VenvPy -m pip install --upgrade pip
  & $VenvPy -m pip install -e ".[dev]"
  if ($LASTEXITCODE -ne 0) { throw "Échec de l'installation des dépendances Python." }
}

# Lance une commande python dans l'environnement choisi.
function Invoke-Py {
  param([Parameter(ValueFromRemainingArguments = $true)]$Args)
  if ($UseUv) { & python -m uv run python @Args }
  else { & (Join-Path $Root ".venv\Scripts\python.exe") @Args }
}

if (-not $SkipProfile) {
  Invoke-Py tools/configure_profile.py
}

if (-not $SkipGcsim) {
  Invoke-Py tools/install_gcsim.py
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "gcsim n'a pas pu être installé automatiquement. Le reste d'Irminsul reste utilisable."
  }
}

if (-not $SkipSources) {
  Invoke-Py -m irminsul.cli update
}

Invoke-Py -m pytest -q

if (-not $NoSchedule) {
  $TaskName = "IrminsulDailyUpdate"
  $ScriptPath = Join-Path $Root "scripts\scheduled-update.ps1"
  $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
  $Trigger = New-ScheduledTaskTrigger -Daily -At 3:17AM
  $Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
  try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Mise à jour quotidienne des sources Irminsul AI" -Force | Out-Null
    Write-Host "Tâche quotidienne installée: $TaskName"
  } catch {
    Write-Warning "Impossible d'installer la tâche quotidienne: $_"
    Write-Warning "La commande manuelle reste: UPDATE_IRMINSUL.bat"
  }
}

Write-Host ""
Write-Host "Installation terminée. Lance maintenant: claude"
Write-Host "Dans Claude Code, accepte une fois le serveur MCP de projet lorsqu'il est demandé."
