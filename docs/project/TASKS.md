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

## Phase 2 — terminée
- [x] Import GOOD branché à l'UI Compte (provenance, fraîcheur, rapport d'anomalies, non-résolus)
- [x] Sélecteur de fichier natif (plugin dialog, permission minimale)
- [x] Fiches Personnages / Armes / Artéfacts (onglets, tables, données scannées)
- [x] **Sidecar Python autonome** (PyInstaller) embarqué (externalBin), protocole borné, Python non requis
- [x] App **packagée** validée (import/affichage/relance/restauration) + CI Windows reproductible
- [ ] (suite) détail par personnage (substats/drapeaux) ; virtualisation des longues listes

## Phase 3 — démarrée
- [x] `data/mechanics/source-registry.json` (registre versionné : règle, sources, statut, confiance, tests) — embarqué dans le sidecar
- [x] Moteur de calcul rapide déterministe (réutilise damage/reaction, traçabilité) + commandes sidecar `quick-calc`/`mechanics` + écran « Calcul rapide » (« Voir le calcul ») + golden tests
- [ ] Réactions additives (aggravate/spread, bloom) ; calcul transformatif dans l'UI ; brancher stats finales du compte
