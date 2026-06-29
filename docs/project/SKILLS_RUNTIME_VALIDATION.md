# SKILLS_RUNTIME_VALIDATION (2026-06-29)

> Validation runtime (§18) : mission test → journalisation → rapport → validation. Skills installés en
> **versions complètes** (autorisation §2/§3), scores SkillSpector = **traçabilité** (cf. SKILLS_SECURITY_SCAN.md),
> limites dures §4 conservées. Emplacement : `duo-agents-fork/.claude/skills/` (isolé, hors PR #3).

## Skills installés (16) — versions épinglées
- **Ingénierie** (alirezarezvani/claude-skills @`4a3c05b`, MIT) : senior-architect, senior-qa, senior-frontend,
  senior-backend, senior-security, code-reviewer, tdd-guide.
- **Design officiels** : frontend-design (anthropics/claude-code @`01f1617`), frontend-design-review (microsoft/skills @`fddb721`, MIT).
- **Suite ui-ux-pro-max** (npm `ui-ux-pro-max-cli` 2.9.0, via `uipro init`) : ui-ux-pro-max, design, design-system,
  ui-styling, brand, banner-design, slides.

## Validation runtime effectuée
| Skill | Mission test | Journalisé | Tests | Statut |
|---|---|---|---|---|
| senior-architect | incrément « messages fiables » (frontières + 1ère correction) | ✅ events/files | 4/4 (node) | **validé → trusted** |
| ui-ux-pro-max | `uipro init` (génération suite) + scan + scope vérifié | ✅ commands/files | scan SkillSpector | **installé**, qualifying |
| tdd-guide | journalisation des tests de l'incrément | ✅ events | — | partiel |
| autres (12) | non encore exercés | — | — | installés, untrusted |

## Garanties
- **Checkpoints réversibles** : chaque étape = commit git du fork (rollback possible).
- **Télémétrie locale par code** (jamais via modèle) : `tools/skill-telemetry/log.py` → `.duo/skill-activity/`.
- **Scope vérifié** : `uipro init` n'a écrit que dans `.claude/skills/` (aucune modif hors périmètre).
- **Aucun secret lu/affiché** ; aucune exfiltration détectée (scan).

## Prochaines validations runtime
senior-backend → senior-security → frontend-design → senior-frontend → frontend-design-review → senior-qa → code-reviewer,
chacun via une mission test bornée + journalisation, au fil des incréments Duo (ordre §14).
