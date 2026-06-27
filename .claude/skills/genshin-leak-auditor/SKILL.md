---
name: Genshin Leak Auditor
description: Analyse un leak (provenance, date, bêta, preuve, corroboration) sans jamais le présenter comme officiel.
argument-hint: "<leak à analyser>"
---
Audite le leak : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §4 et le module leaks/research_policy.
1. **Bannière obligatoire** en tête : `⚠️ LEAK NON CONFIRMÉ — …` (utilise `research_policy.format_leak`).
2. Score le leak via `score_leak` (provenance, preuve, corroboration, track record, précision, stade).
3. Catégorise : très probable / crédible / incertain / rumeur faible / spéculation / réfuté / devenu officiel.
4. Précise : date du leak, version supposée, éléments confirmés/incertains, ce qui peut changer.
5. Ne jamais écrire « officiel / confirmé / définitif / garanti ». La réputation seule ne suffit pas : score l'élément précis. Garde le leak **séparé** du LIVE.
