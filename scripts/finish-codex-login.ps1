# Termine l'auth Codex (navigateur) puis relance le bootstrap Duo. N'affiche aucun token.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { Write-Error "codex absent — lancer d'abord scripts/bootstrap-codex-and-skills.ps1"; exit 1 }

Write-Output "Lancement de l'authentification Codex (une fenetre navigateur peut s'ouvrir)..."
codex login   # sous-commande exacte; ne pas logger la sortie sensible

# Verifier le statut sans exposer de secret
$ok = $false
try { codex login status *> $null; $ok = ($LASTEXITCODE -eq 0) } catch { $ok = $false }
if (-not $ok) { Write-Output "Auth non confirmee. Reessayer la fenetre, puis relancer ce script."; exit 2 }

Write-Output "Auth OK. Test read-only (aucune modification)..."
codex exec --cd "$root" --sandbox read-only --ask-for-approval never --json `
  "Resume uniquement le nom de la branche Git courante et confirme n'avoir modifie aucun fichier."

Write-Output "Reprise Duo..."
& "$PSScriptRoot/resume-duo-after-codex-login.ps1"
