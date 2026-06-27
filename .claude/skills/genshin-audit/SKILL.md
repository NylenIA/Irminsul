---
name: Genshin Project Audit
description: Audit complet du projet ou ciblé (réponse, calcul, équipe, source, leak, fichier GOOD, simulation gcsim) avec sévérités.
argument-hint: "[projet | réponse | calcul | équipe | source | leak | good | gcsim]"
---
Audite : $ARGUMENTS

1. **Audit projet** (défaut) : lance `irminsul audit` (PYTHONPATH=src) → architecture, agents, skills, MCP, dépendances, sources, fraîcheur, import GOOD, gcsim, DPS, tests, docs, sécurité/confidentialité, compat Windows, cohérence des prompts. Classe en CRITIQUE/IMPORTANT/INCOHÉRENCE/RISQUE/OBSOLÈTE/RECOMMANDATION/OK. Rapport écrit dans `data/account/reports/`.
2. **Audit ciblé** : applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §5 à l'objet —
   - *réponse* → `/genshin-answer-auditor` ; *source* → `/genshin-source-verifier` ; *leak* → `/genshin-leak-auditor` ; *good* → `irminsul account import-good` ; *gcsim* → relire la config + hypothèses ; *calcul/équipe* → vérifier buffs, RES, DEF, réaction, version, cohérence transversale.
3. Termine par un compte rendu : constats classés + correctifs + ce qui reste à vérifier.
