---
name: Genshin Farm Planner
description: Crée un plan de farm selon les matériaux réellement possédés et les objectifs de progression.
argument-hint: "<personnage(s) ou objectif>"
---
Plan de farm (objectif : $ARGUMENTS).

1. Charge `data/account/current/materials.json` (matériaux **scannés**) et le profil. Base-toi sur ce qui est **réellement possédé** ; ce qui manque est `[MANQUE]`.
2. Pour chaque objectif (montée niveau, talents, arme) : liste **matériaux disponibles vs manquants**, le domaine/jour de farm, le coût en résine et en Mora.
3. Tiens compte des goulots réels du compte (ex. XP perso/Mora limités, couronnes disponibles).
4. Donne un plan **7 jours** et **30 jours** priorisé par rendement (gain de puissance par résine).
5. Vérifie le patch (jours de domaine, événements). Sépare `[SCAN]/[CALCUL]/[LIVE]`.
