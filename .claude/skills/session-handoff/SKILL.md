---
name: Session Handoff
description: Produit/actualise un état compact de reprise avant compaction ou changement de session (évite de tout réanalyser).
argument-hint: "[jalon courant]"
---
Reprise de session : $ARGUMENTS

1. Mets à jour, **compacts**, les fichiers d'état : `docs/project/STATUS.md` (où on en est + prochaine action), `TASKS.md` (todo/doing/done), `DECISIONS.md` (décisions + raison), `RISKS.md`.
2. Ne recopie ni code ni logs : pointe vers fichiers/symboles (`.irminsul/index/`) et logs (`.irminsul/logs/`).
3. Inclure : jalon terminé, preuve/tests, prochain jalon, blocage réel éventuel.
4. Après mise à jour, `/compact` est sûr. `MASTER_SPEC.md` reste la référence (ne pas recharger sauf ambiguïté).
