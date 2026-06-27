---
name: Project Context Selector
description: Sélectionne de façon ciblée les fichiers, symboles, décisions et tests utiles à une tâche, sans tout lire.
argument-hint: "<tâche ou zone du code>"
---
Contexte ciblé pour : $ARGUMENTS

1. Consulte `.irminsul/index/repo-index.json` (sinon `python scripts/index_repo.py`) pour localiser fichiers + symboles pertinents (ligne).
2. Lis **uniquement** les plages/symboles utiles (mesurer la taille d'abord ; étendre si la tâche l'exige).
3. Croise avec `docs/project/STATUS.md`, `DECISIONS.md`, `TASKS.md` pour l'état courant.
4. Pour un gros JSON (GOOD, gcsim) → `python scripts/peek_json.py` (jamais d'injection complète).
5. Restitue une sélection compacte : fichiers/symboles à ouvrir + raison, sans recopier le code intégral.
