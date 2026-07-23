# Vérifie sur disque les skills Claude attendus (SKILL.md + frontmatter). Echoue si un attendu manque.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$dir = Join-Path $root ".claude/skills"

$expected = @(
  "frontend-design","skill-creator","webapp-testing",
  "senior-architect","senior-backend","senior-security","senior-frontend","senior-qa","code-reviewer","tdd-guide",
  "design","design-system","ui-styling","brand","banner-design","slides","ui-ux-pro-max","frontend-design-review"
)
# Secondaires encore absents (informatif, non bloquant) :
$secondary = @("systematic-debugging","verification-before-completion","find-skills","redesign-existing-projects","web-design-guidelines","emil-design-eng","impeccable","taste-skill")

$missing = @()
foreach ($s in $expected) {
  $md = Join-Path $dir "$s/SKILL.md"
  if (Test-Path $md) {
    if ((Get-Content $md -TotalCount 1) -ne "---") { Write-Output "WARN: $s sans frontmatter --- en tete" }
    else { Write-Output "OK   : $s" }
  } else { $missing += $s }
}
foreach ($s in $secondary) {
  if (Test-Path (Join-Path $dir "$s/SKILL.md")) { Write-Output "INFO : secondaire present: $s" }
  else { Write-Output "INFO : secondaire absent (non bloquant): $s" }
}

if ($missing.Count -gt 0) {
  Write-Error ("Skills attendus manquants: " + ($missing -join ", "))
  exit 1
}
Write-Output ("OK: {0} skills attendus presents." -f $expected.Count)
