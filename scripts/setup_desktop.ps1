# Setup reproductible de l'environnement desktop Irminsul (Windows).
# Comble l'absence locale de Rust/Cargo (requis par Tauri 2). Non destructif.
# Usage : powershell -ExecutionPolicy Bypass -File scripts/setup_desktop.ps1
$ErrorActionPreference = "Stop"

Write-Host "== Node / npm =="
node --version; npm --version

Write-Host "== Rust (rustup) =="
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
  Write-Host "Rust absent → installation via winget (rustup)."
  winget install --id Rustlang.Rustup --source winget --accept-package-agreements --accept-source-agreements
  Write-Host "Relance le terminal puis : rustup default stable"
} else {
  cargo --version
}

Write-Host "== Tauri CLI (local au projet app/) =="
Push-Location (Join-Path $PSScriptRoot "..\app")
npm install --no-audit --no-fund
# La CLI Tauri sera ajoutée comme devDependency quand src-tauri/ sera initialisé :
#   npm install -D @tauri-apps/cli; npx tauri init
Pop-Location

Write-Host "Setup desktop terminé (Rust requiert un redémarrage du terminal s'il vient d'être installé)."
