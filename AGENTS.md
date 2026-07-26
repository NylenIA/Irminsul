# AGENTS.md — règles partagées Claude Code + Codex (Irminsul)

> Compact. Mêmes règles fondamentales que `CLAUDE.md`, sans le recopier. Détail : `docs/project/`.

## Dépôt & branche
- Canonique : `<racine locale>/Irminsul-AI-Claude-Code` · remote `NylenIA/Irminsul`.
- Branche de travail : `feat/irminsul-complete-redesign`. **Ne pas toucher** `main`, `feat/combat-engine-phase3`, `duo-agents-fork`.

## Architecture (local-first)
- Moteur **Python** `src/irminsul/` (KEEP). Desktop **Tauri** `app/`. Web **Next.js 16** `apps/web`.
- Partagé : `packages/ui` (design system « Archive astrale »), `packages/data-access` (Prisma + SQLite **local**, serveur uniquement), `packages/engine-client` (à venir).
- **Aucune donnée privée vers le cloud.** Supabase = futur optionnel. Cf. `docs/project/DECISIONS.md`.

## Commandes
- Web : `npm run build -w @irminsul/web` · `npm run dev -w @irminsul/web`.
- DB : `cd packages/data-access && npx prisma validate|generate|migrate dev` · `npx vitest run`.
- Python : `bash scripts/validate.sh` (Ruff + pytest). Desktop : `npm --prefix app run tauri:dev` (PATH `~/.cargo/bin`).

## Git & sécurité
- Commits atomiques. **Pas de push/PR sans accord.** Pas de `git reset --hard` sur le dépôt principal.
- Aucun secret en clair / dans les logs. Pas de migration destructive. Pas de `npm audit fix --force`.

## Skills (où les lire)
- Claude : `.claude/skills/`. **Codex : `.agents/skills/`.** Chaque skill = `SKILL.md` (frontmatter `name`/`description`).
- Registre de confiance : `docs/skills/SKILL_EFFECTIVENESS.md`. Routage : `docs/skills/SKILL_ROUTING_MATRIX.md`.
- Un skill `untrusted`/`candidate` démarre en **SHADOW/ADVISORY** (sortie revue avant application).

## Duo (superviseur, quand applicable)
- `duo --help` pour les sous-commandes réelles (`run/chat/send/status/limits/doctor`). Dépend de **Codex authentifié**.
- Codex en non-interactif : `codex exec --cd <worktree> --sandbox workspace-write --ask-for-approval never --json` (jamais `--yolo`/`danger-full-access`). Revue lecture seule : `--sandbox read-only`.
- Isolation : sous-mission Codex avec écriture → **worktree dédié**, Claude révise le diff avant intégration.

## Continuité (lire en début de session)
`docs/project/PROJECT_STATE.md` · `NEXT_ACTIONS.md` · `DECISIONS.md` · `SESSION_HANDOFF.md`.

## Définition de « terminé »
Build + typecheck + tests passent (preuve réelle) · pas de placeholder trompeur · pas de fausse donnée · registre & continuité à jour · branches non autorisées intactes.
