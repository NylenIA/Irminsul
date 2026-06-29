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
- **Registre versionné** `data/mechanics/source-registry.json` embarqué dans le sidecar (voyage avec le moteur). Mécaniques `verified` (dégâts, DEF, RES, amplifiantes, additives, transformatives, stats principales d'artéfact 5★, **stats de base perso**) ; `unknown` signalées (**stats de base d'arme** = tâche suivante, réactions Lunaires). live ≠ unknown ≠ leaks.
- **Stats de base perso** (`basestats`) : PV/ATQ/DÉF par niveau+ascension via courbes genshin-db **extraites et committées** (`data/mechanics/character-basestats.json`, provenance commit `acd86e05` + formule + confiance, embarqué dans le sidecar). 119 persos ; Voyageur → aether ; clés hors source signalées non prises en charge ; valeurs validées en jeu (Ayaka 12858, Hu Tao 15552/106). Branché dans `charstats` : base + **stats finales auto**, chaque stat marquée `complete:false` tant que l'arme n'est pas branchée (rien d'inventé).
- **Calcul rapide** déterministe (`quickcalc`) : réactions **amplifiantes + additives (Aggravation/Propagation) + transformatrices**, détail explicable (entrées, stat, multiplicateurs, réaction, DEF, RES, crit, dégâts finaux, version+source+confiance).
- **Connecté au compte** (`charstats`) : sélection d'un personnage importé → stats **exactes issues des artéfacts** (substats réels + table 5★ niv.20) + provenance ; UI préremplit crit/EM, affiche le build et les éléments **non pris en charge** (base perso/arme, effets conditionnels, multiplicateur de talent auto) — sans rien inventer.
- **Stats de base d'ARME** (`weaponstats`, 236 armes) : ATQ de base + stat secondaire par niveau+ascension (`base × courbe + promotion` ; secondaire sans ascension), extraites/committées (`data/mechanics/weapon-basestats.json`, embarquées), croisées EN JEU (Mistsplitter 674/44.1%, Wolf's 608/49.6%, The Catch 509/45.9%). Caps de rareté (1-2★ → niv 70). Registre `weapon_base_stats` = **`probable`** (contre-revue Codex requise pour `verified`).
- **Parcours AUTOMATIQUE complet** : import GOOD → perso → arme+artéfacts → **stats finales (`complete=true`)** = écran du jeu (hors buffs conditionnels). Le champ de saisie ATQ se **masque automatiquement** quand `final_stats.atk.complete`.
- **Validé** : **226 tests Python** (goldens indépendants vs jeu, propriétés, robustesse NaN/inf, non-régression, intégration), Ruff, frontend `tsc` strict + `vite build`, **`cargo test` (5)**. **App packagée** re-validée sans Python : import → perso → **base perso+arme** → **ATQ finale complète** → calcul → relance/restauration (`scripts/test_packaged_app.sh`, `test_sidecar_clean.sh`).
- **Talents** (`talentstats`, 123 persos) : multiplicateurs par niveau étiquetés (libellés exacts du jeu, param→label), Voyageur par élément. **Câblés** dans `charstats` (`talents_detail` au niveau réel) + UI (sélecteur qui remplace la saisie `scaling` pour les talents pris en charge).
- **Registre** : `weapon_base_stats` = **`verified`** (2026-06-29) après revue indépendante R3 (10 armes croisées au wiki en jeu) + extraction reproductible (SHA256 + checkout propre). `character_base_stats` verified ; `talent_multipliers`/réactions Lunaires à statuer.
- **Revues Codex (via Duo)** : R1 (base perso), R2 (correctifs), R3 (armes) → tous `changes-required`, **constats corrigés** (C1–C6 + résidus + #4/#5 ; voir `docs/reviews/`). **R4 (talents) bloquée par quota Codex** → gate de fusion talents en attente.
- **Confidentialité** : mémoire d'agent gitignorée ; vrai UID **retiré** (réécriture des messages limitée à `feat`, `--force-with-lease`, arbre identique ; local+distant propres ; `main`/tags intacts). Repo privé.
- **Incident** `engine.ts` (supprimé hors mission) : restauré ; **isolation Codex read-only** + test d'intégrité dépôt ; scheduler Duo **désactivé**. Cf. `docs/reviews/INCIDENT_engine_ts.md`.

## Livraison PR #3
- **CI verte** (frontend ✅, desktop ✅ sidecar sans Python, test ✅), CLEAN/MERGEABLE. Dernier commit `eff0097`. **NON fusionnée** (critère : parcours automatique stats finales, cf. HANDOFF).

## Prochaine action — Phase 3 (suite) → voir `docs/project/HANDOFF.md`
- **Fait** : base perso + arme (`verified`) ; ATQ finale complète ; talents (module + câblage UI) ; correctifs revues R1–R3 ; confidentialité + incident `engine.ts`.
- **Bloquant fusion** : **revue Codex R4 (talents)** en attente quota (~03:58) ; CI GitHub à confirmer verte ; pas de défaut critique/élevé ouvert.
- **Ensuite** : buffs/sets/passifs d'arme/constellations **conditionnels** (avec conditions explicables), sélection **ennemi** améliorée, puis statuer `talent_multipliers` en `verified` après R4.
