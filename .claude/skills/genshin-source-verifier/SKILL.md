---
name: Genshin Source Verifier
description: Vérifie la fiabilité d'une ou plusieurs sources (tier, date, primaire vs repost, contradictions) avant de s'y fier.
argument-hint: "<source(s) ou affirmation à sourcer>"
---
Vérifie les sources : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §3, et `research_policy.source_quality` / `detect_contradictions`.
1. Classe chaque source par **tier** (A primaire > B technique > C communautaire > D leak).
2. Pénalise : **sans date**, **repost** (vs origine), **secondaire présentée comme primaire**, source morte.
3. Vérifie la **date de publication** vs version du jeu concernée.
4. Si plusieurs sources : signale les **contradictions** (ne pas trancher au hasard ; vérifier dates/versions).
5. Conclus par : source(s) retenue(s), fiabilité, problèmes, et confiance résultante.
