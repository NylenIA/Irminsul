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

## Phase 1 (après la porte) — todo
- [ ] Vérifier dispo toolchain (Node/npm/Rust/Tauri) + versions/licences
- [ ] Si dispo : scaffold Tauri 2 + React/TS strict + Vite ; sinon CI/protocole reproductible
- [ ] SQLite + migrations ; design system local ; sécurité/logs ; CI
