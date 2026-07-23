# Vérifie que le registre des skills correspond à la réalité disque.
# Echoue si un skill marqué installComplete=true n'a pas son SKILL.md, ou si un skill 'absent' apparait sur disque.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
$reg = Get-Content "$root/docs/skills/SKILL_EFFECTIVENESS.json" -Raw | ConvertFrom-Json
$skillsDir = Join-Path $root ".claude/skills"
$problems = @()

foreach ($s in $reg.skills) {
  $onDisk = Test-Path (Join-Path $skillsDir "$($s.skill)/SKILL.md")
  if ($s.installComplete -and -not $onDisk) {
    $problems += "INCOHERENT: '$($s.skill)' marque installComplete mais SKILL.md absent."
  }
  if ((-not $s.installComplete) -and $onDisk) {
    $problems += "INCOHERENT: '$($s.skill)' marque NON installe mais present sur disque."
  }
}

if ($problems.Count -gt 0) {
  $problems | ForEach-Object { Write-Output $_ }
  Write-Error "Registre incoherent avec le disque ($($problems.Count) problemes)."
  exit 1
}
$installed = ($reg.skills | Where-Object { $_.installComplete }).Count
Write-Output "Registre coherent : $installed skill(s) installe(s) confirme(s) sur disque, $($reg.skills.Count - $installed) absent(s)."
