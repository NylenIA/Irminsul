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

## Livraison
- [x] CI verte (frontend/desktop/test) — test handshake MCP scopé Windows ; PR #2 fusionnée (squash) dans `main`.

## Phase 3 — sur `feat/combat-engine-phase3` (PR #3)
- [x] `data/mechanics/source-registry.json` (registre versionné) embarqué dans le sidecar
- [x] Calcul rapide déterministe + commandes sidecar + écran « Calcul rapide » + golden tests
- [x] Réactions **additives** (Aggravation/Propagation) + **transformatrices** dans l'UI
- [x] Connexion compte : sélection perso importé → stats **artéfacts exactes** + provenance ; non-pris-en-charge signalé
- [x] Détail explicable complet ; golden + propriétés + non-régression ; références indépendantes (table 5★)
## Phase 3 — prochaine session (ordre imposé, cf. `docs/project/HANDOFF.md`)
- [x] 1. **Stats de base perso** live, versionnées et sourcées → `src/irminsul/basestats.py` (courbes genshin-db
      extraites/committées + provenance) ; `charstats` calcule auto base + stats finales (marquées INCOMPLÈTES
      tant que l'arme n'est pas branchée) ; sidecar/app packagée re-validés sans Python ; 147 tests
- [ ] 2. Courbes/stats **d'armes** (← EN COURS ENSUITE : débloque ATQ finale complète → retrait saisie ATQ)
- [ ] 3. **Multiplicateurs de talents** par niveau
- [ ] 4. **Stats finales auto** (sans saisie ATQ/scaling pour cas pris en charge)
- [ ] 5. **Buffs/sets/armes/constellations conditionnels** (conditions explicables)
- [ ] 6. Sélection **ennemi** améliorée
- [ ] 7. Golden + property + non-régression
- [ ] 8. **Re-valider le parcours packagé sans Python**
- [ ] Fusion PR #3 quand le parcours stats finales est **automatique** (persos/talents pris en charge) + CI verte
