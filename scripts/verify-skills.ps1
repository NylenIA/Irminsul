# Verifie que les skills attendus sont presents et valides (SKILL.md avec frontmatter).
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$expected = @("frontend-design", "skill-creator", "webapp-testing")
$missing = @()

foreach ($name in $expected) {
  $md = Join-Path $root ".claude/skills/$name/SKILL.md"
  if (-not (Test-Path $md)) { $missing += $name; continue }
  $head = Get-Content $md -TotalCount 1
  if ($head -ne "---") { Write-Output "ATTENTION: $name/SKILL.md sans frontmatter." }
  else { Write-Output "OK: $name" }
}
if ($missing.Count -gt 0) {
  Write-Error ("Skills manquants: " + ($missing -join ", ") + " — voir scripts/install-approved-skills.ps1")
  exit 1
}
Write-Output "Tous les skills attendus sont presents."
