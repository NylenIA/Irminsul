# TASKS

## Phase 0 (porte) — done / doing
- [x] Baseline mesurée + script reproductible
- [x] CLAUDE.md réduit/dédupliqué (< 200 lignes) + règles par chemin
- [x] Infra : index léger, wrapper logs (exit code), projection JSON
- [x] `config/token-budgets.json` (seuils souples)
- [x] Fichiers de reprise (`docs/project/*`)
- [x] Skills orthogonaux (project-context, session-handoff)
- [~] Tests de non-régression infra Phase 0
- [~] Mesure avant/après + rapport + commit de phase

## Phase 1 — en cours
- [x] Vérifier toolchain (Node OK ; Rust absent) + licences (permissives)
- [x] Scaffold frontend Vite+React+TS strict (`app/`) — **build validé** (tsc + vite)
- [x] CI desktop (`.github/workflows/desktop.yml`) + setup Rust (`scripts/setup_desktop.ps1`)
- [ ] `app/src-tauri/` (coque Tauri) — requiert Rust (CI/local)
- [ ] SQLite + migrations ; design system étendu ; logs app

## Phase 2 — todo
- [ ] Brancher l'import GOOD existant (`irminsul.account`) à l'UI Compte (provenance, fraîcheur)
