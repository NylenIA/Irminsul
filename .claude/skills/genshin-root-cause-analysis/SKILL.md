---
name: Genshin Root Cause Analysis
description: Pour une erreur détectée, trouve la cause racine et propose une correction définitive (pas un patch cosmétique).
argument-hint: "<erreur ou incohérence>"
---
Analyse de cause racine : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §6–7.
1. Détermine : quoi / où / depuis quand / cause / fichiers concernés / erreurs similaires ailleurs / risque de régression / comment l'empêcher de revenir.
2. Cherche la **cause racine** (cache ancien, mauvaise priorité de source, parsing, arrondi prématuré, formule incomplète, prompt ambigu, validation absente, mapping de noms, live mélangé au leak, dépendance obsolète, test manquant, doublon de buff, hypothèse cachée).
3. Propose une **correction structurelle** : code/données + prompt + doc + validation + message d'erreur + **test de non-régression** + vérification des fichiers similaires.
4. Journalise dans `CHANGELOG_RESEARCH_AND_FIXES.md`. Jamais de `try/except` masquant, ni valeur inventée.
