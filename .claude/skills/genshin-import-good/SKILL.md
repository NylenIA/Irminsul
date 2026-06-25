---
name: Genshin GOOD Import
description: Analyse un export GOOD de Genshin Optimizer pour accéder au roster, armes et artefacts complets du compte.
argument-hint: "<chemin-vers-export.json>"
---
Inspecte le fichier `$ARGUMENTS` avec `inspect_good_export`. Vérifie le format et résume le compte avant toute optimisation. N'affiche pas inutilement l'intégralité du JSON. Utilise ensuite l'agent `account-optimizer` pour les équipes et l'allocation d'artefacts.
