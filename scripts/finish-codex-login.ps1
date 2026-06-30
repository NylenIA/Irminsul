Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$codexCommand = Get-Command codex -ErrorAction SilentlyContinue
if ($null -eq $codexCommand) {
    throw 'Codex est introuvable. Relancez bootstrap-codex-and-skills.ps1.'
}

Write-Host ('Codex detecte : {0}' -f $codexCommand.Source)
& $codexCommand.Source --version
if ($LASTEXITCODE -ne 0) {
    throw ('Impossible d executer Codex. Code : {0}' -f $LASTEXITCODE)
}

Write-Host ''
Write-Host 'Connexion Codex : terminez la procedure dans le navigateur.'
& $codexCommand.Source login
if ($LASTEXITCODE -ne 0) {
    throw ('La connexion Codex a echoue. Code : {0}' -f $LASTEXITCODE)
}

$resumeScript = Join-Path -Path $PSScriptRoot -ChildPath 'resume-duo-after-codex-login.ps1'
if (-not (Test-Path -LiteralPath $resumeScript)) {
    throw ('Script de reprise introuvable : {0}' -f $resumeScript)
}

Write-Host ''
Write-Host 'Connexion Codex terminee. Lancement de la reprise Duo...'
& $resumeScript
