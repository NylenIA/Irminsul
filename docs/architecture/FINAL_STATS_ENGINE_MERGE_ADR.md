# ADR — Intégration contrôlée du moteur de stats finales (phase3 → redesign)

- **Statut** : accepté et exécuté (commits `4b9de45` port, `19da16a` merge).
- **Contexte** : la branche protégée `feat/combat-engine-phase3` contient le moteur de stats
  finales (`charstats.compute_final_stats`). Verrou pour rotations chiffrées, comparateur,
  recommandations, détail personnage. À intégrer **sans merge aveugle** de toute la branche.

## Décision
Portage **fichier par fichier** dans un worktree isolé (`feat/integrate-final-stats-engine`),
validé par pytest, puis mergé `--no-ff` dans `redesign`. Modules portés :
`basestats.py`, `weaponstats.py`, `talentstats.py`, `charstats.py`, `account_ipc.py` (dispatch)
+ données committées (`data/mechanics/*.json`) + tests.

## Carte de dépendances (vérifiée)
```
charstats.compute_final_stats / character_payload
  ├─ basestats   (character_base_stats + character-basestats.json)
  ├─ weaponstats (weapon-basestats.json)
  ├─ talentstats (talent-multipliers.json)
  └─ account.load_current        (déjà présent en redesign — non porté)
account_ipc.dispatch("character-stats") ── expose charstats au CLI et au sidecar
```
`paths.py` et `account.py` existaient déjà en redesign : **non touchés** (aucun conflit).

## Contrats préservés
- Le contrat TS `EngineClient` (coup direct/réactions) reste **inchangé**.
- Nouveau contrat **additif** `final-stats/1.0` (`FinalCharacterStats`, cellules
  `{value, complete, missing}`) — n'altère aucun contrat existant.
- Frontière : UI → Server Action → **sidecar Python** (`character_final_stats`) → `charstats`.
  Pas de repli TS (le calcul de stats finales n'existe qu'en Python) ; erreur typée sinon.

## Invariants du moteur (raison du choix : défensif par conception)
Gardes NaN/Infinity ; arme non supportée/invalide → `complete=false` + `missing` explicite
(jamais de 0 silencieux) ; stat principale d'artéfact non calculée → propagée à la bonne
cellule ; `complete` global seulement si écran du jeu reproductible. **Aucune stat inventée.**

## Alternatives rejetées
- **Merge complet de phase3** : amènerait des changements non liés (leaks, mcp_server, quickcalc)
  → risque + revue plus lourde. Rejeté.
- **Réécriture TS du moteur de stats** : duplication de formules, dérive de parité. Rejeté —
  le Python reste la source de vérité, exposée par sidecar.

## Preuves
pytest **192 passed** (redesign post-merge) · sidecar `character_final_stats` validé bout-en-bout
(Mavuika C0 : ATQ 2377.52, CR 22.8 %, `complete=true`) · adapter TS `normalizeFinalStats` 4/4.
