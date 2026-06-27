---
name: Genshin Abyss Dual Teams
description: Construit deux équipes simultanées pour l'Abîme sans réutiliser aucun personnage, arme ni artéfact.
argument-hint: "<contraintes ou contenu d'Abîme>"
---
Construis deux équipes simultanées (contexte : $ARGUMENTS).

1. Charge le compte (`data/account/current/`). **Persos/armes/artéfacts possédés uniquement** ; exclus les `unresolvedCharacters`.
2. Contrainte stricte d'**allocation exclusive** : un personnage, une arme et un artéfact ne peuvent servir que dans **une** seule des deux équipes (cf. `ExclusiveAllocator` dans `irminsul.account`). Aucune équipe ne doit dépendre d'un objet déjà attribué à l'autre.
3. Optimise le **total simultané**, pas une seule équipe : si un buffeur clé (ex. Furina) ne peut être que d'un côté, choisis l'affectation qui maximise les deux moitiés.
4. Donne pour chaque côté : équipe, rotation, ER, armes/artéfacts exacts, forces mono/multi-cible, et **ce qui manque** (ex. set d'artéfacts à dédoubler).
5. Vérifie le patch, fais auditer par `source-auditor`. Sépare les types de données.
