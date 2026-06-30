# Installe les skills AUDITES (sources/versions de docs/skills/WEB_SKILLS_LOCK.json).
# Chaque 'skills add' demande confirmation (pas de -y agressif ici). Verifier le nom AVANT (--list).
$ErrorActionPreference = "Stop"

# Skills officiels deja installes (idempotent : --list pour verifier sans reinstaller).
$approved = @(
  @{ repo = "https://github.com/anthropics/skills";            skill = "skill-creator" },
  @{ repo = "https://github.com/anthropics/skills";            skill = "webapp-testing" },
  @{ repo = "https://github.com/vercel-labs/agent-skills";     skill = "web-design-guidelines" }
)

foreach ($s in $approved) {
  Write-Output "→ Verification du nom dans $($s.repo) :"
  npx --yes skills@latest add $s.repo --list
  Write-Output "→ Pour installer : npx skills add $($s.repo) --skill $($s.skill) --copy"
  Write-Output ""
}
Write-Output "Skills tiers (obra/pbakaus/leonxlnx/emilkowalski) : auditer le SKILL.md AVANT, puis ajouter ici."
