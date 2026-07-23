# Quality gates (sans démarrer de service cloud)

## Commandes (état réel)
| Gate | Commande | Statut vérifié |
|---|---|---|
| Build web | `npm run build -w @irminsul/web` | ✅ PASS (Next 16.2.9, TS OK) |
| Prisma valide | `cd packages/data-access && npx prisma validate` | ✅ PASS |
| Prisma génère | `... npx prisma generate` | ✅ PASS |
| Migration SQLite | `... npx prisma migrate dev` / `migrate status` | ✅ PASS (init_local_app_data) |
| Test repository | `... npx vitest run` | voir PROJECT_STATE (en validation) |
| Python moteur | `bash scripts/validate.sh` (Ruff + pytest, 96 tests) | à relancer sur cette branche |
| Hook idempotent | `pwsh scripts/verify-session-context.ps1` (20 appels) | à exécuter |

## Scripts racine souhaités (à câbler dans un package.json de tâches)
`lint`, `typecheck`, `test`, `test:unit`, `test:e2e`, `test:a11y`, `build`, `verify`.
`verify` orchestre lint+typecheck+test+build **sans** service cloud.

## Exigences avant « phase terminée »
0 erreur TS · build OK · tests unit + repository OK · pas de secret versionné · pas de placeholder trompeur ·
pas de migration destructive · MCP préservés · skills découverts · continuité à jour.
