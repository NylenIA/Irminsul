# Hook SessionStart Irminsul — IDEMPOTENT. Lit l'état, ne modifie RIEN, n'installe RIEN.
# À enregistrer dans .claude/settings.json (événements: startup, resume, clear, compact).
# Ne lance jamais npm/npx/git clone/Supabase. Termine vite.
$ErrorActionPreference = "SilentlyContinue"
$root = (Resolve-Path "$PSScriptRoot/../..").Path
Set-Location $root

$branch = (git rev-parse --abbrev-ref HEAD 2>$null)
$remote = (git remote get-url origin 2>$null)

Write-Output "── Irminsul · contexte de session ──"
Write-Output "Depot  : $root"
Write-Output "Remote : $remote"
Write-Output "Branche: $branch"
if ($branch -eq "main" -or $branch -eq "feat/combat-engine-phase3") {
  Write-Output "ATTENTION: branche '$branch' — le redesign vit sur feat/irminsul-complete-redesign. Ne pas y travailler le redesign."
}

$skills = @(Get-ChildItem "$root/.claude/skills" -Directory -ErrorAction SilentlyContinue).Name
Write-Output ("Skills projet ({0}): {1}" -f $skills.Count, ($skills -join ", "))

if (Test-Path "$root/.mcp.json") {
  try {
    $servers = ((Get-Content "$root/.mcp.json" -Raw | ConvertFrom-Json).mcpServers.PSObject.Properties.Name) -join ", "
    Write-Output "MCP configures: $servers"
  } catch { Write-Output "MCP: .mcp.json illisible" }
}

function Show-Head($path, $n, $title) {
  if (Test-Path $path) {
    Write-Output "── $title ──"
    Get-Content $path -TotalCount $n
  }
}
Show-Head "$root/docs/project/PROJECT_STATE.md" 16 "PROJECT_STATE (extrait)"
Show-Head "$root/docs/project/NEXT_ACTIONS.md" 14 "NEXT_ACTIONS (extrait)"
Write-Output "── Decisions: LOCAL-FIRST; cloud/Supabase optionnel plus tard; ne pas toucher main/phase3/duo-agents-fork. ──"
