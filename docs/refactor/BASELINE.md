# BASELINE — mesures avant refonte (2026-06-29)

> Instantané **mesuré** (lecture seule), branche `feat/combat-engine-phase3` @ HEAD.
> Sert de référence avant/après pour la branche `refactor/pro-ui-security`. `measured` vs `to-measure` explicites.

## Code (LOC mesuré)
- **Python** : 4383 LOC (`src/irminsul/`). Top : `account.py` 721, `basestats.py` 349, `cli.py` 308,
  `charstats.py` 304, `research_policy.py` 267, `weaponstats.py` 256, `talentstats.py` 250.
- **Frontend** : 966 LOC (`app/src`). Top : `QuickCalc.tsx` **413**, `engine.ts` 264, `Account.tsx` 215, `App.tsx` 62.
- **Rust** : `lib.rs` 230 LOC, **8 commandes IPC** (`account_*`, `quick_calc`, `mechanics`, `character_stats`).

## Tests (measured)
- **226 tests Python** (21 fichiers) + `test_repo_integrity.py`. Rust : 5 tests. Frontend : **0 test composant/e2e** (gap).
- Couverture forte : moteur/données (basestats/weaponstats/talentstats/charstats/damage/reaction/sidecar).
  Couverture faible/absente : UI React, accessibilité, clavier, responsive, E2E.

## Dépendances
- **Python** : httpx, mcp, pydantic, pyyaml, rapidfuzz, rich, tenacity, typer (ranges pinnés). **Pas de lockfile Python** (gap supply-chain — `uv.lock`/`pip-tools` à introduire).
- **Frontend** : `package-lock.json` présent ✓. **Rust** : `Cargo.lock` présent ✓.
- Aucune dépendance UI lourde (pas de lib de composants) — design « maison » minimal.

## Build / packaging (measured, ordres de grandeur)
- `vite build` ≈ 0.7–1.2 s ; bundle JS ≈ 158 kB (gzip ≈ 51 kB).
- `tauri build` (Rust release + MSI + NSIS) ≈ 1 min 30 (incrémental, Rust inchangé) ; installeurs MSI/NSIS.
- Sidecar PyInstaller onefile ≈ 9.6 Mo (stdlib + données mécaniques embarquées : registre + 3 JSON sourcés).

## À MESURER (non encore instrumenté)
- Temps de démarrage app (cold/warm) ; mémoire ; latence par appel sidecar (extraction onefile par requête).
- Perf des listes (artéfacts/persos) sans virtualisation ; temps de première peinture.
- Couverture de tests chiffrée (pas de `--cov` configuré).
