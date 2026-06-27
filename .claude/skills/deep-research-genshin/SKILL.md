---
name: Deep Research Genshin
description: Recherche multi-sources approfondie sur un sujet Genshin incertain/récent, avec dates, hiérarchie de sources et confiance explicite.
argument-hint: "<question>"
---
Recherche approfondie : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §2–3, §9.
1. Vérifie d'abord la **version live** (`irminsul status`) et la base locale (`search_knowledge`).
2. Lance **plusieurs requêtes différentes** (pas le premier résultat) ; cherche primaires (A) puis secondaires (B/C).
3. Compare **dates** et **versions**, cherche errata/corrections et **contradictions**, comprends pourquoi les sources divergent, recoupe ≥ 2 sources indépendantes.
4. Sépare faits / hypothèses / leaks. Ne fabrique pas les données manquantes → `safe_unknown`.
5. Rends le format §9 : Conclusion · Version · Données vérifiées · Hypothèses · Sources (date+type) · Contradictions · Leaks · Confiance · Limites.
