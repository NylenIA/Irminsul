# PROJECT_STATE — état de reprise (continuité inter-sessions)

> Source de vérité compacte. Lire en début de session avec NEXT_ACTIONS.md.
> Ne pas transformer en journal géant — archiver périodiquement.

## Entrée 2026-06-30
- **Dépôt** : `C:/Users/akuon/IA Genshin/Irminsul-AI-Claude-Code` · remote `NylenIA/Irminsul`.
- **Branche** : `feat/irminsul-complete-redesign` (basée sur `main` bfb6a04). Ne pas toucher `main`, `feat/combat-engine-phase3`, ni `duo-agents-fork`.
- **Dernier commit** : `ce0a355` feat(web): Next.js 16 shell.
- **Objectif courant** : architecture hybride (desktop Tauri préservé + nouvelle app web Next.js) + audit + continuité. Supabase/Prisma **non retenus** sans besoin produit (voir blocages).

### Fait (vérifié + committé)
- Préflight + dépôt canonique (`docs/project/CANONICAL_REPO.md`), baseline (`BASELINE_STATUS.md`).
- Audit §3 complet (`docs/audit/*`) : matrice KEEP/MIGRATE/BLOCKED.
- Monorepo npm (root `package.json` workspaces) sans casser `app/` Tauri.
- **App web Next.js 16.2.9** (`apps/web`) : build vérifié (`Compiled successfully`, TS OK, routes statiques).
- Correctifs préservés : Vite EBUSY (`app/vite.config.ts`), `score_leak` (warnings hors 0-5).
- Skill `frontend-design` installé. `.mcp.json` intact (`irminsul` seul).

### Blocages (décision propriétaire / environnement)
- **R1** : Supabase/Prisma = base cloud non justifiée par une fonctionnalité ; conflit local/offline/privé. → quel besoin serveur concret ? sinon abandonner.
- **R2** : Supabase non connectable ici (Docker + CLI absents, auth interactive indispo).
- **R3** : pont moteur (`engine.ts` enrichi) seulement sur `feat/combat-engine-phase3` → web « vraies données » nécessite fusion PR #3 ou `packages/engine-client`.
- Outillage absent : SkillSpector, `/impeccable`, pnpm.

### Tests à l'instant
- Next build : PASS (vérifié). Python : 96 tests (non relancés sur cette branche ce jour — à mesurer).
- 2 vulns modérées transitives (postcss via next) : **non corrigées** (le fix `--force` rétrograde next → cassant). Acceptées, à revoir à la mise à jour de Next.
