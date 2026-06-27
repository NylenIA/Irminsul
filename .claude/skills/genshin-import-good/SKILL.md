---
name: Genshin GOOD Import
description: Importe, valide, normalise et compare un export GOOD (Inventory Kamera / Genshin Optimizer) vers data/account.
argument-hint: "<chemin-vers-export.json>"
---
Importe l'export GOOD `$ARGUMENTS` dans le pipeline de compte.

1. Lance `irminsul account import-good "$ARGUMENTS" --snapshot-date <YYYY-MM-DD>` (PYTHONPATH=src). L'import est **idempotent** (même SHA-256 → pas de doublon), copie le brut en **lecture seule** dans `data/account/raw/`, écrit les snapshots datés, met à jour `data/account/current/` et génère `data/account/reports/import-validation-<date>.md`.
2. **Ne modifie jamais** le fichier GOOD d'origine et **n'envoie jamais** le compte à un service externe.
3. Lis le rapport de validation et signale les anomalies par sévérité (INFO/WARNING/ERROR/BLOCKING). Rappelle les `unresolvedCharacters` (ex. Traveler) — ne pas les utiliser en reco principale.
4. Si un snapshot précédent existe, présente le **diff** (nouveaux persos, constellations, niveaux, talents, armes, artéfacts, matériaux).
5. Enchaîne avec l'agent `account-optimizer` (équipes, allocation exclusive arme/artéfact) ou les skills `/genshin-account`, `/genshin-team`, `/genshin-dps`.

N'affiche pas l'intégralité du JSON : résume.
