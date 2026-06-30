# Inventaire réel des skills Claude Code (preuve disque 2026-06-30)

> Vérifié dans `.claude/skills/`. Corrige les anciennes tables. `~/.claude/skills/` (user) : vide.
> Vérif : `pwsh scripts/verify-claude-skills.ps1` (échoue si registre ≠ disque).

## Installés + détectés (18, hors skills Genshin internes)
| Skill | Source (provenance) | Statut |
|---|---|---|
| frontend-design | anthropics (fourni) | installed_verified |
| skill-creator, webapp-testing | anthropics/skills | installed_verified |
| senior-architect, senior-backend, senior-security, senior-frontend, senior-qa, code-reviewer, tdd-guide | `alirezarezvani/claude-skills` @ `4a3c05b` (bootstrap) | installed_verified |
| design, design-system, ui-styling, brand, banner-design, slides, ui-ux-pro-max | `ui-ux-pro-max-cli` (npm 2.9.0) — **provenance à reconfirmer par hash** | installed_but_source_to_verify |
| frontend-design-review | microsoft (revendiqué) — **provenance exacte à confirmer** | installed_but_source_to_verify |

## Absents (secondaires — ne bloquent pas le produit)
`systematic-debugging`, `verification-before-completion`, `find-skills`, `redesign-existing-projects`,
`web-design-guidelines`, `emil-design-eng`, `Impeccable`, `Taste Skill` → **missing** (sources à résoudre/auditer).
`frontend-design-review` Microsoft : si la source exacte reste introuvable → `blocked_source_unresolved`
(créer `irminsul-frontend-design-review` via skill-creator, sans prétendre Microsoft).

## Missions réelles (cette phase) — routage appliqué
- **frontend-design** + **senior-frontend** + **webapp-testing** → Team Lab + `packages/ui` (frontend §5.3).
- **tdd-guide** → règle « un perso ≠ deux emplacements » (test ajouté).
- **senior-qa** → Playwright E2E + axe a11y.
- Revues `code-reviewer` / `senior-security` → docs de revue (en cours).

## À reconcilier
`SKILL_EFFECTIVENESS.json` (encore daté d'avant l'install des 15) doit être régénéré pour passer
les skills installés de `absent` → `candidate`, et `qualifying` ceux ayant une mission réelle + tests.
