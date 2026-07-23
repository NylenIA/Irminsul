# Audit des skills web (manuel, reproductible)

> SkillSpector indisponible → audit manuel : source, auteur, lecture du SKILL.md, scripts/hooks,
> dépendances, commandes destructrices, verdict. Les skills tournent avec les pleins droits de l'agent.

## Installés et découverts (`.claude/skills/`)
| Skill | Source | Auteur | Contenu | Scripts/hooks | Verdict |
|---|---|---|---|---|---|
| frontend-design | fichier fourni par le propriétaire | Anthropic (officiel) | guidance markdown pure | aucun | **APPROVED** |
| skill-creator | github.com/anthropics/skills | Anthropic (officiel) | guidance + utilitaires de création de skill | scripts d'aide, pas de réseau opaque | **APPROVED** |
| webapp-testing | github.com/anthropics/skills | Anthropic (officiel) | toolkit Playwright (test UI local) | utilitaires Playwright | **APPROVED** |

Méthode d'install utilisée : `npx skills add <repo> --skill <name> --copy` (copie de fichiers, pas de symlink ;
revue du SKILL.md avant usage). `.mcp.json` inchangé après install (vérifié).

## Demandés, non encore installés (autorisés par l'utilisateur) → `scripts/install-approved-skills.ps1`
| Skill | Source présumée | Statut | Raison |
|---|---|---|---|
| web-design-guidelines | vercel-labs/agent-skills | PENDING | à installer (officiel vercel-labs) |
| verification-before-completion, systematic-debugging | obra/superpowers | PENDING | auteur connu ; revue de contenu avant install |
| impeccable | pbakaus/impeccable | PENDING | dépend des commandes `/impeccable` indisponibles ici ; utilité limitée |
| design-taste-frontend, redesign-existing-projects | leonxlnx/taste-skill | PENDING | tiers moins connu ; revue de contenu requise |
| emil-design-eng | emilkowalski/skills | PENDING | auteur connu ; revue de contenu |
| skills Next.js/React/TS/Prisma/Playwright/Vitest/a11y/perf/sécurité/Tauri/monorepo | à résoudre via `find-skills` | PENDING | noms exacts à résoudre (ne pas inventer ; cf. leçon `figma-implement-design` inexistant) |

## Garde-fous
- Toujours **vérifier l'existence réelle** du nom de skill (`skills add <repo> --list`) avant install : plusieurs noms cités n'existent pas tels quels.
- Ne jamais installer un skill embarquant un binaire opaque ou un postinstall réseau non audité.
- Réinstallation ≠ découverte : installer **une fois**, le hook SessionStart ne réinstalle rien.
