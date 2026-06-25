param([switch]$RemoveEnvironment)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TaskName = "IrminsulDailyUpdate"

$Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Task) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "Tâche quotidienne supprimée: $TaskName"
} else {
  Write-Host "Aucune tâche quotidienne Irminsul trouvée."
}

if ($RemoveEnvironment) {
  $Venv = Join-Path $Root ".venv"
  if (Test-Path $Venv) {
    Remove-Item -Recurse -Force $Venv
    Write-Host "Environnement Python local supprimé."
  }
}

Write-Host "Les fichiers du projet et tes données locales n'ont pas été supprimés."
Write-Host "Pour tout effacer, supprime ensuite manuellement le dossier Irminsul AI."
