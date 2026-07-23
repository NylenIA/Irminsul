# Carte des dépendances (résumé)

> Prérequis (prompt §2.1) avant tout déplacement de fichiers en monorepo.

## Frontend desktop (app/)
- `app/src/main.tsx` → `App.tsx` → `views/Account.tsx`, `views/QuickCalc.tsx` → `engine.ts`.
- `engine.ts` → `@tauri-apps/api` `invoke()` + `@tauri-apps/plugin-dialog` → commandes Rust.
- Couplage Tauri : `engine.ts` est **le seul** point de couplage UI↔natif → un futur package `engine-client` doit l'abstraire pour qu'une UI web puisse cibler une autre implémentation (API locale).

## Natif → moteur
- `app/src-tauri/src/lib.rs` lance le sidecar (binaire `externalBin`) ; protocole borné (id, erreurs typées, timeout, taille max).
- Sidecar = `src/irminsul/*` empaqueté ; pas d'import croisé app↔src en TS (frontière nette).

## Moteur Python (src/irminsul/) — graphe interne
- `damage`/`reaction` (formules) ← `quickcalc`, `team_optimizer`.
- `account`/`good` (import GOOD) ← `charstats` ← `basestats`/`weaponstats`/`talentstats` (courbes committées).
- `team_optimizer` ← profils intégrés + `config/support_profiles.yaml` + `data/account/current`.
- `mcp_server` expose le tout (outils MCP). `enka`, `gcsim`, `leaks`, `source_sync`/`status` indépendants.

## Services externes
- **Runtime app** : AUCUN (offline). 
- **Dev/Claude Code** : MCP `irminsul` (stdio).
- **Optionnel non implémenté** : Claude API (assistant, Phase 5 MASTER_SPEC).

## Conséquence migration
Frontière UI↔moteur déjà propre (`engine.ts` + protocole sidecar). Une UI web peut réutiliser le moteur **sans** toucher au Python, à condition d'exposer une **interface stable** (package `engine-client`). C'est le seul travail d'intégration réellement nécessaire — pas une base de données.
