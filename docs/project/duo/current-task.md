# Mission Codex active (via `duo run`)

## R3 — Revue indépendante, LECTURE SEULE, des STATS DE BASE D'ARME (à lancer dès quota Codex rétabli)

**Objectif** : auditer l'incrément « stats de base d'arme » + branchement ATQ finale complète.

**Périmètre d'analyse (lecture seule, NE RIEN MODIFIER)** :
- `src/irminsul/weaponstats.py`, `tools/extract_weapon_basestats.py`
- `data/mechanics/weapon-basestats.json`, `data/mechanics/source-registry.json` (entrée `weapon_base_stats`)
- `src/irminsul/charstats.py` (`compute_final_stats` : intégration arme, drapeau `complete`)
- `tests/test_weaponstats.py`, `tests/test_charstats.py`
- UI : `app/src/engine.ts`, `app/src/views/QuickCalc.tsx`

**Points prioritaires** :
1. Exactitude ATQ = `base × courbe_atk[niveau] + promotion[ascension]` ; secondaire = `base_secondary ×
   courbe_secondary[niveau]` (sans ascension). **Comparer un échantillon à des références INDÉPENDANTES**
   (en jeu / Genshin Optimizer / KQM) : ATQ de base + stat secondaire à L90 pour 5–10 armes variées
   (épée/arc/catalyseur/lance/claymore ; secondaires CR/CD/ATQ%/ER/EM/PHYS/DEF%/HP% ; rareté 1–5★).
2. Caps de niveau par rareté (1-2★ → niv 70), paires niveau/ascension impossibles rejetées.
3. Unités de la stat secondaire (pourcentage ×100 vs Maîtrise brute) ; `FIGHT_PROP_NONE` = sans secondaire.
4. `compute_final_stats` : ATQ% appliqué à (ATQ base perso + ATQ base arme) ; secondaire d'arme ajouté au
   bon total ; `complete=true` SEULEMENT si arme prise en charge ET aucune stat principale d'artéfact manquante ;
   aucune valeur par défaut silencieuse ; pas de NaN/inf.
5. Provenance reproductible (commit source), registre cohérent (`weapon_base_stats` = `probable` → vérifier
   s'il peut passer `verified`).

**Format** : pour chaque constat → sévérité, fichier:lignes, reproduction, cause, correction minimale,
test de non-régression. Verdict final : `approve` / `changes-required` / `blocked`.
Écrire le rapport UNIQUEMENT dans `docs/reviews/CODEX_PR3_WEAPONSTATS_REVIEW.md`. Aucun commit/push/fusion.
