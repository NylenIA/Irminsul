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
- [x] `app/src-tauri/` (coque Tauri 2) — **build release local OK** (irminsul.exe + MSI + NSIS) après install VS Build Tools
- [ ] SQLite + migrations ; design system étendu ; logs app

## Phase 2 — en cours
- [x] Import GOOD branché à l'UI Compte (provenance, fraîcheur, rapport d'anomalies, non-résolus)
- [x] Sélecteur de fichier natif (plugin dialog, permission minimale)
- [x] Fiches Personnages / Armes / Artéfacts (onglets, tables, données scannées)
- [ ] Détail par personnage (substats/drapeaux) ; virtualisation des longues listes
