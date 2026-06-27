---
name: Genshin Regression Tester
description: Ajoute/exécute des tests de non-régression après une correction et vérifie que rien d'autre ne casse.
argument-hint: "<correction ou module concerné>"
---
Tests de non-régression : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §7, §16.
1. Écris un test qui **échoue avant** la correction et **passe après** (verrou).
2. Couvre si pertinent : info récente → recherche, leak ≠ officiel, donnée obsolète détectée, sources contradictoires signalées, source sans date pénalisée, repost < origine, erreur de calcul, version incorrecte, confiance cohérente avec les preuves.
3. Lance `bash scripts/validate.sh` (Ruff + pytest). Corrige tout échec, puis relis le diff.
4. Confirme : tests ajoutés, résultats, et qu'aucun module dépendant n'est cassé.
