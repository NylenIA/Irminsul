---
description: Règles compte joueur GOOD/Enka (chargées quand on touche l'import compte)
paths:
  - "src/irminsul/account.py"
  - "src/irminsul/enka.py"
  - "tests/test_account_import.py"
  - "data/account/**"
---
# Compte joueur (GOOD / Enka)

- **Ne jamais** injecter un GOOD complet, la base SQLite ou les artefacts complets dans le contexte → `scripts/peek_json.py` pour une projection.
- GOOD : valider le schéma, normaliser **sans perte silencieuse**, détecter doublons/valeurs inconnues, rapport d'import + retour arrière. `id` Inventory Kamera **non fiable** → ids internes stables.
- Provenance par donnée si possible : `value, source, sourceType, gameVersion, retrievedAt, confidence, isLeak, isUserProvided, hash`.
- GOOD et Enka **non fusionnés silencieusement** : priorité explicite par champ, origine conservée.
- Ne jamais supposer une possession absente du scan. `unresolvedCharacters` (ex. Traveler) exclus des recos principales.
- Données compte = `data/account/` **gitignoré** ; ne jamais committer ni exposer (UID/pseudo = perso).
