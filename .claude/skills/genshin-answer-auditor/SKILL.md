---
name: Genshin Answer Auditor
description: Audite une réponse complète avant envoi (faits, sources, dates, calculs, cohérence, leaks, confiance).
argument-hint: "<réponse à auditer>"
---
Audite la réponse : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §5, §9 (et délègue à `source-auditor` si besoin).
1. **Faits** : chaque affirmation importante a une source primaire/B datée ? Sinon → marquer ou rechercher.
2. **Calculs** : multiplicateurs, buffs (pas dupliqués/oubliés), RES, formule DEF, réaction, unités, niveaux de talents, énergie/rotation réalistes.
3. **Cohérence transversale** : même version/perso/arme/raffinement/niveau/set/cible/RES/hypothèses (`/genshin-consistency-checker`).
4. **Leaks** : bannière présente, jamais « officiel »; séparés du LIVE.
5. **Confiance** : niveau explicite cohérent avec les preuves ; limites listées.
6. Rends : erreurs détectées, corrections, et le verdict (prêt / à corriger).
