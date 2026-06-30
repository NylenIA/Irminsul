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

## CI / tests
- Le test d'intégration MCP `test_launcher_stdio_handshake` cible une **régression stdio Windows** (`os.execv`) → `skipif` hors Windows (sur ubuntu CI il n'est pas pertinent et renvoyait 0 outil). Le **contrat « 10 outils » reste vérifié toutes plateformes** par `test_mcp_exposes_exactly_ten_tools` (unitaire). `validate.sh` (Windows) exécute la suite complète, intégration comprise.

## Phase 2 — sidecar moteur (distribuable)
- **Empaquetage** : PyInstaller **onefile** (moteur = stdlib uniquement → bundle petit/fiable). Sortie `irminsul-sidecar-<triple>.exe` via `tools/build_sidecar.py`. Embarqué par Tauri **`externalBin`** ; `app/src-tauri/binaries/` **gitignoré** (régénéré par le script/CI, binaire lourd).
- **Exécution** : Rust spawn direct du sidecar (std::process + `wait-timeout`), **pas** de plugin shell → surface minimale (le frontend n'exécute aucun process arbitraire, seulement nos commandes `account_*`). `CREATE_NO_WINDOW` sous Windows.
- **Protocole** : un coup par requête (robuste, isolé), stdin JSON `{id,method,params}` → stdout JSON `{id,ok,result|error}`. Bornes : taille requête (2 Mo) + réponse (32 Mo), **timeout 30 s + kill**, erreurs structurées. Aucun secret en argument (tout sur stdin). Compromis assumé : léger surcoût d'extraction onefile par appel (acceptable pour des ops compte peu fréquentes).
- **Chemins** : sidecar résolu **à côté de l'exe** (dev = target/debug, installé = dossier app) ; données dans **`app_data_dir`** (jamais le dépôt ni le PATH Python).
- **Tests** : Python `test_sidecar.py` (JSON invalide, méthode inconnue, requête vide/trop grande, chemin espaces/Unicode, gros GOOD) ; Rust (`parse_response`, sidecar absent, aller-retour réel, timeout) ; scripts `test_sidecar_clean.sh` (sans Python) et `test_packaged_app.sh` (import/affichage/relance/restauration sur binaires release).

## Refonte web / local-first (2026-06-30) — branche `feat/irminsul-complete-redesign`
- **D-LF1 — LOCAL-FIRST maintenant, cloud optionnel plus tard** (décision propriétaire). Données privées (compte, inventaire, calculs, simulations, préférences, logs) **restent sur la machine**. Supabase = fonctions **futures et optionnelles** (auth, sync volontaire, sauvegarde chiffrée, profils publics, partage, communauté), désactivées par défaut. Aucune donnée privée vers le cloud.
- **D-LF2 — Architecture hybride additive** : `apps/web` (Next.js 16) ajoutée sans détruire le desktop Tauri (`app/`) ni le moteur Python. Monorepo npm (`apps/*`, `packages/*`).
- **D-LF3 — Base de branche `main`** (pas phase3). Pont moteur enrichi absent → slice web via adaptateur `EngineClient` (mock isolé) tant que PR #3 non fusionnée.
- **D-LF4 — Persistance locale = Prisma + SQLite** (`packages/data-access`) derrière l'interface `TeamRepository`. **Prisma 6 retenu** (moteur embarqué, `new PrismaClient()` + `url=env`) plutôt que Prisma 7 (impose un *driver adapter* + dépendance native risquée sous Windows). Reproductibilité par lockfile.
- **D-LF5 — Sécurité deps** : pas de `npm audit fix --force` (rétrograderait Next). Scripts d'install autorisés package par package, méthode officielle.
- **D-LF6 — Ne pas toucher** `main`, `feat/combat-engine-phase3`, `duo-agents-fork`. Pas de push/PR sans accord.
