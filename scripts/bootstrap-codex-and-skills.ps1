# Bootstrap reproductible : Codex CLI + skills audités (sources/commits épinglés).
# Idempotent. N'affiche aucun secret. S'arrête uniquement pour l'auth Codex interactive.
# NOTE: l'agent Claude ne peut PAS exécuter la copie des skills dans .claude/.agents
#       (controle de securite "self-modification"). CE script, lance par l'utilisateur, le fait.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$cache = Join-Path $env:USERPROFILE ".cache/irminsul-skills/alirezarezvani-claude-skills"
$repo = "https://github.com/alirezarezvani/claude-skills.git"
$commit = "4a3c05b69e64f4925f7fc65c88890f614f79caf0"
$skills = @("senior-architect","senior-backend","senior-security","senior-frontend","senior-qa","code-reviewer","tdd-guide")

# 1) Codex CLI
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
  $v = (npm view '@openai/codex' version).Trim()
  Write-Output "Installation @openai/codex@$v ..."
  npm install --global "@openai/codex@$v"
}
Write-Output ("codex: " + (codex --version))

# 2) Source skills (clone au commit exact, idempotent)
if (-not (Test-Path "$cache/.git")) {
  git clone --filter=blob:none $repo $cache
}
git -C $cache fetch --depth 1 origin $commit
git -C $cache checkout --detach $commit
if ((git -C $cache rev-parse HEAD) -ne $commit) { throw "Commit inattendu (attendu $commit)." }

# 3) Audit minimal (red-flags dans des scripts executables)
$flags = Select-String -Path "$cache/engineering-team/skills/*/*" -Pattern "curl |wget |Invoke-WebRequest|rm -rf|child_process|ACCESS_TOKEN|api[_-]?key|password" -ErrorAction SilentlyContinue
if ($flags) { Write-Output "AUDIT: motifs a revoir :"; $flags | Select-Object -First 10 | ForEach-Object { Write-Output "  $_" } }
else { Write-Output "AUDIT: aucun script executable a risque detecte (contenu = guidance markdown)." }

# 4) Installation Claude (.claude/skills) + Codex (.agents/skills) + hash
$lock = @{}
foreach ($s in $skills) {
  $src = Join-Path $cache "engineering-team/skills/$s"
  foreach ($scope in @(".claude/skills", ".agents/skills")) {
    $dst = Join-Path $root "$scope/$s"
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Recurse -Force "$src/*" $dst
  }
  $hash = (Get-FileHash (Join-Path $root ".claude/skills/$s/SKILL.md") -Algorithm SHA256).Hash
  $lock[$s] = @{ source = $repo; commit = $commit; sha256 = $hash }
  Write-Output "Installe: $s (sha256 $($hash.Substring(0,16))...)"
}
$lock | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $root "docs/skills/SKILL_INSTALLATION_LOCK.local.json")
Write-Output "OK. Lock local ecrit. Lancer ensuite: scripts/finish-codex-login.ps1"
