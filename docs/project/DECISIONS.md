# DECISIONS

- **Politique centrale unique** : `docs/RESEARCH_POLICY.md` (héritée). On dédoublonne au lieu de recopier.
- **CLAUDE.md = index lean** : architecture/commandes/priorités/politique-contexte + liens. Détail domaine → `.claude/rules/` (chargées par chemin) et skills à la demande.
- **Infra déterministe en scripts**, pas en prose modèle : mesure, index, compression de logs, projection JSON.
- **Logs hors contexte** : `.irminsul/logs/` ; au modèle = exit code réel + erreurs uniques + résumé + chemin. Jamais de pipe qui masque le code de sortie.
- **Gros fichiers jamais injectés** : GOOD/SQLite/gcsim/builds → `peek_json.py` / extraction ciblée.
- **Budgets souples** (`config/token-budgets.json`) : jamais de réduction de qualité/test/source.
- **Modèle/effort adaptatifs** : éco (exploration) → équilibré (dev) → avancé (archi/sécurité/theorycraft/debug) ; monter si risque.
- **Skills** : on n'a pas supprimé les commandes Genshin existantes (chargées à la demande, coût permanent nul) ; on ajoute seulement les capacités orthogonales utiles. Le prompt caching réel est **préparé** (préfixe stable tools→system→messages) et sera finalisé avec la gateway Claude (Phase 5).

## Phase 1 — stack & toolchain (vérifié 2026-06-27)
- Toolchain réelle : **Node v24.18 + npm 11.16 présents** ; **Rust/Cargo ABSENTS**. → Frontend buildable localement ; **build Tauri (Rust) reporté en CI** (`.github/workflows/desktop.yml`) + `scripts/setup_desktop.ps1` (rustup). Validation desktop complète marquée **non exécutée localement** (cf. RISKS.md, MASTER_SPEC §466).
- Stack retenue : **Vite + React 18 + TypeScript strict** (frontend), **Tauri 2** (coque desktop, IPC/stdio — pas de serveur HTTP exposé), **moteur Python existant conservé** comme service local typé (sidecar empaqueté plus tard). Licences permissives (MIT / Apache-2.0).
- Frontend scaffold `app/` **build validé** : `tsc --noEmit` (strict) + `vite build` OK. `node_modules/`, `dist/` gitignorés.
