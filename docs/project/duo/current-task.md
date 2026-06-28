# Mission Codex active (via `duo run`)

## R1 — Revue indépendante, LECTURE SEULE, du diff PR #3 (stats de base perso)

**Objectif** : auditer l'incrément « stats de base personnage » de la PR #3 par rapport à `main`.

**Périmètre d'analyse (diff `main..HEAD`)** :
- `src/irminsul/basestats.py`, `src/irminsul/charstats.py`
- `tools/extract_basestats.py`, `data/mechanics/character-basestats.json`
- `data/mechanics/source-registry.json`
- `tests/test_basestats.py`, `tests/test_charstats.py`
- intégration UI : `app/src/engine.ts`, `app/src/views/QuickCalc.tsx`

**Points prioritaires** :
1. Exactitude des stats de base (formule `base × courbe[niv] + promotion[asc]`), unités de la stat
   d'ascension (EM brut vs % ×100), résolution de clés (Voyageur→aether), bornes niveau/ascension.
2. Provenance/versionnage des données extraites (commit genshin-db, fraîcheur, reproductibilité du script).
3. Calcul `final_stats` : drapeau `complete`, listes `missing`, absence de valeur par défaut silencieuse.
4. Disparition conditionnelle de la saisie ATQ (UI) liée à `final_stats.atk.complete`.
5. Validation numérique (NaN/inf/hors-plage), double comptage, golden **indépendants** de la formule du code.
6. Cohérence du registre de sources (statut/confiance/sources/tests pour `character_base_stats`).

**Contraintes STRICTES** :
- **NE MODIFIER AUCUN fichier de code/test/données.**
- Seule écriture autorisée : le rapport `docs/reviews/CODEX_PR3_BASESTATS_REVIEW.md`.
- Interdiction de `git commit`, `git push`, fusion, modification de `main`.

**Format du rapport** (`docs/reviews/CODEX_PR3_BASESTATS_REVIEW.md`) — pour chaque constat :
`sévérité (critique/élevé/moyen/faible) · fichier:lignes · reproduction · cause probable · correction minimale · test de non-régression`.
Terminer par un verdict global : `approve` / `changes-required` / `blocked`.
