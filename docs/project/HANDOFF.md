# HANDOFF — reprise de session (sans refaire l'audit)

> Lire ce fichier + `MASTER_SPEC.md` suffit pour reprendre. Ne pas réauditer les phases passées.

## Contexte git
- **Branche** : `feat/combat-engine-phase3` (NE PAS en créer d'autre).
- **PR** : **#3** → https://github.com/NylenIA/Irminsul/pull/3 (OPEN, **NON fusionnée**).
- **Base** : `main` = `bfb6a04` (PR #2 fusionnée : Phases 0-2).
- **Dernier commit** : voir `git log` (stats de base perso ajoutées après `25e00ab`).
- **CI PR #3** : ✅ verte (frontend, desktop avec sidecar testé sans Python, test).

## Fonctions réellement terminées (validées)
- **Phases 0-2 (dans `main`)** : infra efficacité tokens ; app desktop **Tauri 2** ; **sidecar moteur autonome** (PyInstaller, **Python non requis**) ; écran Compte (import GOOD, provenance, fiches perso/armes/artéfacts) ; installeurs **MSI/NSIS**.
- **Phase 3 (PR #3)** :
  - **Registre** `data/mechanics/source-registry.json` (embarqué dans le sidecar) : mécaniques `verified` (dégâts, DEF, RES, amplifiantes, **additives**, transformatives, **stats principales artéfact 5★**) ; `unknown` signalées (stats de base perso, réactions Lunaires).
  - **Calcul rapide** (`quickcalc`) : réactions **amplifiantes + additives (Aggravation/Propagation) + transformatrices**, détail explicable (entrées, stat, multiplicateurs, réaction, DEF, RES, crit, dégâts finaux, **version+source+confiance**).
  - **Connexion compte** (`charstats`) : sélection perso importé → **stats exactes des artéfacts** (substats réels + table 5★ niv.20) + provenance ; UI préremplit crit/EM ; éléments **non pris en charge** affichés.
  - Sidecar : méthodes `characters`, `character-stats`, `quick-calc`, `mechanics` ; commandes Tauri correspondantes.
  - **Stats de base perso** (`src/irminsul/basestats.py`) : PV/ATQ/DÉF par niveau+ascension = `base × courbe[niv] + promotion[asc]` ; courbes + valeurs **extraites** de genshin-db (`tools/extract_basestats.py`) vers `data/mechanics/character-basestats.json` **committé + embarqué** dans le sidecar (provenance : commit `acd86e05`, formule, confiance). 119 persos, Voyageur→aether, hors-source signalé. `charstats` calcule auto base + **stats finales** (`final_stats`, chaque stat `complete:false` tant que l'arme n'est pas branchée). UI : panneau base sourcée + préremplissage hors arme ; champ ATQ masqué auto quand `atk.complete`.

## Tests exécutés (tous verts)
- `bash scripts/validate.sh` → **Ruff + 118 tests Python**.
- Rust : `cargo test` dans `app/src-tauri` → **5 tests** (parse, sidecar absent, aller-retour réel, timeout).
- Parcours packagé sans Python : `bash scripts/test_packaged_app.sh` (import→perso→stats→calcul→relance/restauration) ; `bash scripts/test_sidecar_clean.sh`.

## Limitations EXACTES (signalées, jamais inventées)
1. **Stats de base perso ET arme = OK** (calculées, sourcées, croisées en jeu). ATQ finale **complète**
   (`final_stats.atk.complete=true`) pour perso+arme pris en charge ; saisie ATQ masquée auto. Reste :
   `weapon_base_stats` = **`probable`** (contre-revue Codex indépendante requise pour `verified`, quota en attente).
2. **Multiplicateur de talent manuel** (table de talents non branchée) → saisie du `scaling`. ← PROCHAIN
3. **Passifs d'arme / sets 4p / constellations CONDITIONNELS** non appliqués (situationnels, hors fiche).
3. **Buffs / sets 4p / passifs d'arme / constellations conditionnels NON appliqués**.
4. Table des **stats principales d'artéfact limitée au 5★ niveau 20** (autres rareté/niveau → listées « non calculées »).
5. **Réactions Lunaires** (Nod-Krai) = `unknown`, refusées par le calcul.

## Où travailler (fichiers clés)
- Moteur : `src/irminsul/{charstats,quickcalc,reaction,damage,account,account_ipc,sidecar}.py`
- Registre : `data/mechanics/source-registry.json`
- Pont Rust : `app/src-tauri/src/lib.rs` · UI : `app/src/views/QuickCalc.tsx`, `app/src/engine.ts`
- Tests : `tests/test_{charstats,quickcalc,reaction,sidecar,account_ipc}.py`
- Build/scripts : `tools/build_sidecar.py`, `scripts/{validate.sh,test_sidecar_clean.sh,test_packaged_app.sh}`

## Reprendre (commandes)
```
git checkout feat/combat-engine-phase3
bash scripts/validate.sh                  # ruff + 118 tests
PYTHONUTF8=1 python tools/build_sidecar.py # régénère le sidecar (binaries/ gitignoré)
(cd app && PATH=~/.cargo/bin:$PATH npx tauri build)   # exe + MSI + NSIS
bash scripts/test_packaged_app.sh         # parcours packagé sans Python
```

## PROCHAINE tâche (ordre imposé, même branche/PR #3)
**(1) Stats de base perso = FAIT** (`basestats.py`, extraction committée, registre `verified`, branché dans `charstats`, packagé re-validé).

**(2) Stats de base d'ARME = FAIT** (`weaponstats.py` + `tools/extract_weapon_basestats.py` →
`data/mechanics/weapon-basestats.json`, 236 armes, embarqué) ; branché dans `compute_final_stats`
→ **ATQ finale complète** ; registre `weapon_base_stats` = `probable` (→ `verified` après contre-revue Codex, quota en attente).

**Prochain fichier/tâche** : **(3) multiplicateurs de talents** — extraire `data/sources/genshin-db/src/data/stats/talents.json`
(par niveau de talent 1..15) vers `data/mechanics/` (committé + embarqué + provenance), distinguer NA/skill/burst,
brancher dans le calcul pour **retirer la saisie manuelle du `scaling`** pour les talents pris en charge (signaler le reste).

Puis dans l'ordre : (4) **stats finales auto** complètes [FAIT pour ATQ] ;
(5) **buffs/sets/armes/constellations conditionnels** avec conditions explicables ; (6) sélection **ennemi** améliorée ;
(7) golden + property + non-régression ; (8) **re-valider le parcours packagé sans Python**.

## Critère de fusion PR #3 (ne pas fusionner avant)
Parcours **automatique** pour persos/talents pris en charge :
import GOOD → perso → arme/artéfacts → **stats finales** → talent+niveau → ennemi/réaction →
**dégâts** → **détail explicable**. Tout non-pris-en-charge reste explicitement marqué.
