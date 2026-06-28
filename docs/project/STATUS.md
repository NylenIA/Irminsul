# STATUS

**Phase courante : 3 — Moteur de combat** (sur `feat/combat-engine-phase3`, PR #3). Phases 0-2 livrées (PR #2 fusionnée dans `main`).

## Fait
- Spec autoritative placée (`docs/project/MASTER_SPEC.md`).
- Baseline contexte mesurée (`.irminsul/index/baseline.json`, voir `BASELINE.md`).
- Infra déterministe : `scripts/measure_context.py`, `index_repo.py`, `run_logged.py` (préserve exit code), `peek_json.py`.
- `config/token-budgets.json` (seuils souples).
- CLAUDE.md allégé + dédupliqué ; règles par chemin `.claude/rules/{dps,account}.md`.
- Skills orthogonaux : `project-context`, `session-handoff` (research-verify ≈ `deep-research-genshin`).
- `.irminsul/logs/` + `.irminsul/index/` opérationnels (gitignorés).

## En cours
- Tests de non-régression de l'infra Phase 0 ; mesure avant/après ; rapport + commit de phase.

## Phase 1 — terminée
- Stack : Vite+React+TS strict, **Tauri 2**, moteur Python conservé. Rust 1.96 + VS Build Tools installés.
- **Build Windows local produit** : `irminsul.exe` + installeurs **MSI** et **NSIS** (cf. RISKS résolu). CI desktop active.

## Phase 2 — terminée (app distribuable)
- Écran **Compte** branché au moteur GOOD réel (provenance, fraîcheur, anomalies, non-résolus) + sélecteur natif + fiches Personnages/Armes/Artéfacts. Aucune donnée factice.
- **Sidecar moteur autonome** (PyInstaller onefile, stdlib only) embarqué via `externalBin`, exécuté par Rust (protocole stdin/stdout borné : id, erreurs typées, timeout+kill, taille max). **Python NON requis** chez l'utilisateur.
- Données dans le dossier app (`app_data_dir`), pas le dépôt ni le PATH Python.
- **App packagée validée** (release exe + sidecar) : import → affichage → relance → restauration, sans Python (`scripts/test_packaged_app.sh`). Installeurs MSI (12 Mo) + NSIS (11 Mo) avec sidecar embarqué. CI Windows reproductible (`desktop.yml`).

## Phase 3 — en cours (PR #3)
- **Registre versionné** `data/mechanics/source-registry.json` embarqué dans le sidecar (voyage avec le moteur). Mécaniques `verified` (dégâts, DEF, RES, amplifiantes, additives, transformatives, stats principales d'artéfact 5★) ; `unknown` signalées (stats de base perso, réactions Lunaires). live ≠ unknown ≠ leaks.
- **Calcul rapide** déterministe (`quickcalc`) : réactions **amplifiantes + additives (Aggravation/Propagation) + transformatrices**, détail explicable (entrées, stat, multiplicateurs, réaction, DEF, RES, crit, dégâts finaux, version+source+confiance).
- **Connecté au compte** (`charstats`) : sélection d'un personnage importé → stats **exactes issues des artéfacts** (substats réels + table 5★ niv.20) + provenance ; UI préremplit crit/EM, affiche le build et les éléments **non pris en charge** (base perso/arme, effets conditionnels, multiplicateur de talent auto) — sans rien inventer.
- **Validé** : 118 tests Python (goldens indépendants, propriétés, non-régression, intégration), Ruff, frontend `tsc` strict, `cargo check`. **App packagée** re-validée sans Python : import → personnage → stats → calcul → relance/restauration (`scripts/test_packaged_app.sh`).

## Livraison PR #3
- **CI verte** (frontend ✅, desktop ✅ sidecar sans Python, test ✅), CLEAN/MERGEABLE. Dernier commit `eff0097`. **NON fusionnée** (critère : parcours automatique stats finales, cf. HANDOFF).

## Prochaine action — Phase 3 (suite) → voir `docs/project/HANDOFF.md`
- **Prochain fichier** : `src/irminsul/basestats.py` (+ courbes `data/sources/genshin-db/src/data/curve`).
- **Prochaine tâche** : stats de **base perso live, versionnées et sourcées** → calcul **auto** des stats finales (sans saisie ATQ). Puis : courbes d'armes, multiplicateurs de talents, stats finales auto, buffs/sets/constellations conditionnels, ennemi, tests, re-validation packagée.
