# PROJECT_STATE — état de reprise (continuité inter-sessions)

> Source de vérité compacte. Lire en début de session avec NEXT_ACTIONS.md.
> Ne pas transformer en journal géant — archiver périodiquement.

## Entrée 2026-06-30
- **Dépôt** : `<racine locale>/Irminsul-AI-Claude-Code` · remote `NylenIA/Irminsul`.
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

### Reprise 2026-06-30 (sans bloquer)
- **Prisma 6 + SQLite local** (`packages/data-access`) : validate/generate/migrate **OK**, **test repository Vitest PASS** (sauvegarde→recharge→supprime une équipe). Prisma 7 écarté (driver adapter + dép. native risquée Windows).
- **MCP next-devtools** configuré dans `.mcp.json` (irminsul préservé) — état **READY_FOR_APPROVAL** (`/mcp` = action utilisateur unique).
- **Skills** installés + découverts : frontend-design, skill-creator, webapp-testing. Reste documenté dans `docs/skills/` + `scripts/install-approved-skills.ps1`.
- **Continuité** : hook `SessionStart` idempotent + DECISIONS/ARCHITECTURE/QUALITY_GATES/SESSION_HANDOFF.
- **Avancement reproductible** : **MVP 50 % · Vision 48 %** (`scripts/project_progress.py`).

### Pilote moteur (2026-07-01, Fable)
- **Routeur Duo livré** (fork `feat/mandatory-delegation-model-router`, commit `a36edc9` par Codex gpt-5.5, 36/36 tests ×3, revue acceptée `22e6cba`). Incident worktree récupéré via cache-tree.
- **ADR Team Lab ↔ moteur** accepté (`docs/architecture/TEAM_LAB_COMBAT_ENGINE_ADR.md`) : frontière unique `EngineClient`, moteur Python = source de vérité.
- **`packages/engine-client`** (`8a03790`) : contrat + portage TS fidèle de `calculate_direct_hit`, **parité prouvée** (5 goldens générés du moteur Python, 1e-9, 7/7 tests), provenance + hypothèses obligatoires.

### Tests à l'instant
- Next build : PASS. Prisma repository : PASS (5, Vitest). E2E Playwright : 6 PASS. **engine-client : 7/7 PASS**. Duo fork : 36/36 ×3. Python : 96 tests (non relancés sur cette branche ce jour — à mesurer).
- 2 vulns modérées transitives (postcss via next) : **non corrigées** (le fix `--force` rétrograde next → cassant). Acceptées, à revoir à la mise à jour de Next.
