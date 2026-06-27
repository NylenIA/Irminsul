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

## Phase 1 — démarrée
- Toolchain vérifiée (Node OK, Rust absent). Stack : Vite+React+TS strict, Tauri 2 (CI), moteur Python conservé.
- Frontend `app/` scaffoldé et **build validé localement** (tsc strict + vite). CI desktop + setup Rust en place.

## Prochaine action
- Initialiser `app/src-tauri/` (coque Tauri) + activer le job CI Tauri — nécessite Rust (CI ou setup local).
- Puis Phase 2 (données compte : brancher l'import GOOD existant à l'UI Compte).
