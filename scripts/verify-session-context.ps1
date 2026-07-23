# Vérifie que le hook SessionStart est idempotent (20 appels) et ne modifie rien.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$hook = "$root/.claude/hooks/irminsul-session-start.ps1"
if (-not (Test-Path $hook)) { Write-Error "Hook absent: $hook"; exit 1 }

# Empreinte de l'arbre de travail avant
$before = (git -C $root status --porcelain) -join "`n"
1..20 | ForEach-Object { & pwsh -NoProfile -File $hook *> $null }
$after = (git -C $root status --porcelain) -join "`n"

if ($before -ne $after) {
  Write-Error "NON IDEMPOTENT: l'etat git a change apres 20 appels du hook."
  exit 1
}
Write-Output "OK: 20 appels du hook, aucun changement d'etat git (idempotent)."
