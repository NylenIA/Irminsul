---
name: Genshin Upgrade Prioritizer
description: Classe les améliorations possibles par rendement attendu, à partir du compte réel et des matériaux disponibles.
argument-hint: "<budget, contrainte ou objectif>"
---
Classe les améliorations (contexte : $ARGUMENTS).

1. Charge le compte (`irminsul account overview` + `data/account/current/`). Utilise les **drapeaux d'équipement** (armes sous-montées, artéfacts incomplets, couronnes crit manquantes) comme base de gains.
2. Sépare : **gains gratuits** (swap d'arme/artéfact déjà possédé, 0 résine), **gains à coût matériaux** (montée niveau/talents), et **gains nécessitant un nouvel objet** `[MANQUE]`.
3. Propose explicitement : meilleures améliorations à **budget limité**, et meilleures améliorations **sans invoquer de nouveau personnage**.
4. Classe par **gain de puissance par unité de coût** (résine/Mora/XP), en tenant compte des matériaux scannés.
5. N'améliore pas les `unresolvedCharacters`. Sépare `[SCAN]/[CALCUL]/[THEORYCRAFT]/[SIM]`.
