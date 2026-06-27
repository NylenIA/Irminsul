# STATUS

**Phase courante : 0 — Fondation d'efficacité des tokens** (porte de passage avant Phase 1).

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

## Phase 3 — démarrée
- **Registre versionné des mécaniques** `data/mechanics/source-registry.json` (5 mécaniques cœur : dégâts, DEF, RES, réactions amplifiantes/transformatives ; sources KQM, statut `verified`, tests liés). Embarqué dans le sidecar (`--add-data`, `sys._MEIPASS`) → voyage avec le moteur.
- **Moteur de calcul rapide** déterministe `irminsul.quickcalc` (réutilise `damage`/`reaction`, traçabilité) exposé via le sidecar (`quick-calc`, `mechanics`) + écran **« Calcul rapide »** avec « Voir le calcul ».
- Tests : `test_quickcalc.py` (golden indépendant 3946.15, réaction ×2, intégrité registre, déterminisme) ; smoke sidecar quick-calc OK sans Python.

## Prochaine action
- Étendre le registre (réactions additives : aggravate/spread, bloom), exposer le calcul réaction transformative dans l'UI, brancher les stats finales du compte au calcul rapide.
