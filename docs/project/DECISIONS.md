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

## Phase 3 — stats : honnêteté d'abord (décision)
- On calcule **exactement** ce qui est dérivable du GOOD (artéfacts : substats réels + table fixe 5★ niv.20, `verified`). Tout le reste (stats de **base** perso/arme, talents auto, buffs/sets/constellations conditionnels, réactions Lunaires) est **signalé non pris en charge / `unknown`** — jamais approximé. Séparation **live ≠ unknown ≠ leaks** appliquée dans le registre.
- ~~**Prochaine étape (next session)** : intégrer des stats de base live…~~ **`superseded` 2026-06-28** : stats de base **perso** faites (`basestats`, commit 5167954) ; reste l'**arme** (T2).

## Phase 3 — correctifs revue Codex (2026-06-28)
- **Validation numérique stricte** (C3/§5.5) : NaN/inf rejetés à toutes les frontières (substats GOOD, `compute_final_stats`, `calculate_direct_hit`, `basestats`). Décision : une donnée corrompue est **signalée/rejetée**, jamais propagée silencieusement.
- **Paires niveau/ascension impossibles rejetées** (C1) : on n'extrapole pas une valeur fausse sur des données incohérentes (erreur explicite).
- **Reproductibilité des données extraites** (C6) : `extracted_at` dérive du **commit source** (pas `date.today()`) → fichier byte-identique à source égale.
- **Golden indépendants** (§5.6) : les goldens de base sont ancrés sur des **valeurs en jeu** (Ayaka 12858, Hu Tao 15552/106), pas sur la formule du code.

## Collaboration Claude Code / Codex via Duo (2026-06-28)
- **Claude = lead/orchestrateur** (décide, implémente, teste, trie, commit, PR) ; **Codex = réviseur indépendant** (lecture seule via `duo run`) / worker isolé borné. Codex ne push/merge/main jamais. Cf. `docs/project/AGENT_BOARD.md`.
- **Gate de fusion** : tout changement mathématique/sécurité critique exige une **contre-revue Codex** avant fusion (§7).
- **Confidentialité mémoire (§5.1)** : `.claude/agent-memory/` contient des données personnelles → **retiré du suivi Git + gitignoré** (mémoire LOCALE). Historique **publié** (origin/main, origin/feat) propre (placeholders) ; vrai UID seulement dans des **commits pendants locaux** (reflog) → purge locale possible mais **soumise à autorisation** (aucune réécriture d'historique sans accord).

## CI / tests
- Le test d'intégration MCP `test_launcher_stdio_handshake` cible une **régression stdio Windows** (`os.execv`) → `skipif` hors Windows (sur ubuntu CI il n'est pas pertinent et renvoyait 0 outil). Le **contrat « 10 outils » reste vérifié toutes plateformes** par `test_mcp_exposes_exactly_ten_tools` (unitaire). `validate.sh` (Windows) exécute la suite complète, intégration comprise.

## Phase 2 — sidecar moteur (distribuable)
- **Empaquetage** : PyInstaller **onefile** (moteur = stdlib uniquement → bundle petit/fiable). Sortie `irminsul-sidecar-<triple>.exe` via `tools/build_sidecar.py`. Embarqué par Tauri **`externalBin`** ; `app/src-tauri/binaries/` **gitignoré** (régénéré par le script/CI, binaire lourd).
- **Exécution** : Rust spawn direct du sidecar (std::process + `wait-timeout`), **pas** de plugin shell → surface minimale (le frontend n'exécute aucun process arbitraire, seulement nos commandes `account_*`). `CREATE_NO_WINDOW` sous Windows.
- **Protocole** : un coup par requête (robuste, isolé), stdin JSON `{id,method,params}` → stdout JSON `{id,ok,result|error}`. Bornes : taille requête (2 Mo) + réponse (32 Mo), **timeout 30 s + kill**, erreurs structurées. Aucun secret en argument (tout sur stdin). Compromis assumé : léger surcoût d'extraction onefile par appel (acceptable pour des ops compte peu fréquentes).
- **Chemins** : sidecar résolu **à côté de l'exe** (dev = target/debug, installé = dossier app) ; données dans **`app_data_dir`** (jamais le dépôt ni le PATH Python).
- **Tests** : Python `test_sidecar.py` (JSON invalide, méthode inconnue, requête vide/trop grande, chemin espaces/Unicode, gros GOOD) ; Rust (`parse_response`, sidecar absent, aller-retour réel, timeout) ; scripts `test_sidecar_clean.sh` (sans Python) et `test_packaged_app.sh` (import/affichage/relance/restauration sur binaires release).
