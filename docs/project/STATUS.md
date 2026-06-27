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

## Phase 2 — en cours
- Écran **Compte** branché au moteur GOOD réel (provenance, fraîcheur, rapport d'anomalies, non-résolus).
- **Import par sélecteur de fichier natif** (plugin dialog, perm. minimale).
- Fiches **Personnages / Armes / Artéfacts** (onglets, tables) sur données scannées. Aucune donnée factice.

## Prochaine action
- Détail par personnage (artéfacts/substats, drapeaux d'investissement) ; virtualisation des longues listes.
- Puis Phase 3 (moteur de combat : registre des mécaniques + calcul rapide dans l'app).
