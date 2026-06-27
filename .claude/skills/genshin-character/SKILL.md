---
name: Genshin Character Analysis
description: Analyse un personnage possédé (build réel, armes et artéfacts disponibles, équipes possibles) à partir du compte importé.
argument-hint: "<nom du personnage>"
---
Analyse le personnage : $ARGUMENTS

1. Charge le compte normalisé (`data/account/current/`, ou `irminsul account overview`). **Utilise uniquement** les données scannées ; si le perso est absent du scan, dis-le (`[MANQUE]`) sans rien inventer. Si c'est un `unresolvedCharacter` (Traveler), refuse une reco sérieuse.
2. Résume son build **réel** `[SCAN]` : niveau, ascension, constellation, talents, arme (clé/niveau/raffinement), artéfacts (sets, slots, main stats), drapeaux d'équipement.
3. Liste les **meilleures armes et artéfacts disponibles dans l'inventaire** (pas idéaux théoriques) qui amélioreraient ce perso.
4. Vérifie le patch/fraîcheur, puis propose ses **équipes possibles** avec les persos possédés (délègue à `theorycrafter` si besoin).
5. Sépare `[SCAN] [CALCUL] [HYP] [THEORYCRAFT] [SIM] [LIVE]`. Termine par les améliorations classées par rendement.
