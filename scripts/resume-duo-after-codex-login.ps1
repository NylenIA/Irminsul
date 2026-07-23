# Reprise Duo apres auth Codex : verifs -> test read-only -> mission reelle de revue -> reprise produit.
# Ne fait AUCUNE integration risquee sans revue. Ne tue pas de process en masse.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$runtime = Join-Path $root ".duo/runtime"
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$codexCmd = (Get-Command "codex.cmd" -ErrorAction SilentlyContinue).Source
if (-not $codexCmd) { $codexCmd = (Get-Command "codex" -ErrorAction SilentlyContinue).Source }
$duoCmd = (Get-Command "duo.cmd" -ErrorAction SilentlyContinue).Source
if (-not $duoCmd) { $duoCmd = (Get-Command "duo" -ErrorAction SilentlyContinue).Source }

function Quote-ProcessArgument {
  param([Parameter(Mandatory=$true)][string]$Value)

  if ($Value.Length -eq 0) { return '""' }
  if ($Value -notmatch '[\s"]') { return $Value }
  return '"' + ($Value -replace '"','\"') + '"'
}

function Invoke-CodexReadOnlyJson {
  param(
    [Parameter(Mandatory=$true)][string]$WorkingDirectory,
    [Parameter(Mandatory=$true)][string]$Prompt,
    [Parameter(Mandatory=$true)][string]$OutputFile,
    [Parameter(Mandatory=$true)][string]$Label
  )

  $baseName = [System.IO.Path]::GetFileNameWithoutExtension($OutputFile)
  $stderrFile = Join-Path $runtime "$baseName.stderr.txt"
  $utf8NoBom = New-Object System.Text.UTF8Encoding $false
  $arguments = @("exec", "--cd", "$WorkingDirectory", "--sandbox", "read-only", "--json", "-")

  $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
  $processStartInfo.FileName = $codexCmd
  $processStartInfo.Arguments = (($arguments | ForEach-Object { Quote-ProcessArgument $_ }) -join " ")
  $processStartInfo.WorkingDirectory = $WorkingDirectory
  $processStartInfo.UseShellExecute = $false
  $processStartInfo.RedirectStandardInput = $true
  $processStartInfo.RedirectStandardOutput = $true
  $processStartInfo.RedirectStandardError = $true

  $process = [System.Diagnostics.Process]::Start($processStartInfo)
  $stdoutTask = $process.StandardOutput.ReadToEndAsync()
  $stderrTask = $process.StandardError.ReadToEndAsync()
  $promptBytes = [System.Text.Encoding]::UTF8.GetBytes($Prompt)
  $process.StandardInput.BaseStream.Write($promptBytes, 0, $promptBytes.Length)
  $process.StandardInput.Close()
  $process.WaitForExit()

  [System.IO.File]::WriteAllText($OutputFile, $stdoutTask.Result, $utf8NoBom)
  [System.IO.File]::WriteAllText($stderrFile, $stderrTask.Result, $utf8NoBom)
  $exitCode = $process.ExitCode

  if ($exitCode -ne 0) {
    Write-Error "$Label a echoue avec le code $exitCode. Voir $stderrFile et $OutputFile."
  }
}

# 1) Pre-requis
foreach ($pair in @(@("codex",$codexCmd), @("duo",$duoCmd))) {
  if (-not $pair[1]) { Write-Error "$($pair[0]) absent"; exit 1 }
}
Write-Output ("codex " + (& $codexCmd --version) + " | duo " + (& $duoCmd --version))

# 2) Test read-only Codex (preuve d'auth)
$authCheckFile = Join-Path $runtime "codex-auth-check.json"
$authPrompt = "Reponds exactement sur une seule ligne : CODEX_AUTH_OK READ_ONLY. N'utilise aucun outil, aucune commande, aucun fichier."
Invoke-CodexReadOnlyJson -WorkingDirectory "$root" -Prompt "$authPrompt" -OutputFile "$authCheckFile" -Label "Test auth Codex"
[System.IO.File]::ReadLines($authCheckFile, [System.Text.Encoding]::UTF8) | Select-Object -First 5

# 3) Mission reelle a faible risque : revue read-only du TeamRepository Prisma
Write-Output "Mission Codex (read-only) : revue du TeamRepository..."
$repoFile = Join-Path $root "packages/data-access/src/repositories/team-repository.ts"
$testFile = Join-Path $root "packages/data-access/tests/team-repository.test.ts"
$repoSource = Get-Content -LiteralPath $repoFile -Raw
$testSource = Get-Content -LiteralPath $testFile -Raw
$reviewPrompt = @"
Revue en lecture seule du TeamRepository Prisma.

Important :
- Ne modifie aucun fichier.
- N'appelle pas PowerShell, Get-Content, rg, git, npm, ni aucun outil shell.
- Analyse uniquement le contenu fourni ci-dessous.
- Cherche : validation des entrees, gestion d'erreurs, transactions, tests manquants, separation serveur/client.
- Retourne des findings actionnables avec severite, fichier, zone approximative, risque et correctif propose.

Fichier: packages/data-access/src/repositories/team-repository.ts
~~~ts
$repoSource
~~~

Fichier: packages/data-access/tests/team-repository.test.ts
~~~ts
$testSource
~~~
"@
$reviewFile = Join-Path $runtime "codex-review-team-repository.json"
Invoke-CodexReadOnlyJson -WorkingDirectory "$root/packages/data-access" -Prompt "$reviewPrompt" -OutputFile "$reviewFile" -Label "Revue Codex TeamRepository"
Write-Output "Revue ecrite dans .duo/runtime/ (gitignore). Claude doit la lire et trier les findings avant tout correctif."

# 4) Reprendre le produit (Team Lab)
Write-Output "Etape suivante produit : page apps/web/src/app/team-lab (cf. docs/project/NEXT_ACTIONS.md)."

