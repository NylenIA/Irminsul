# Explicabilité des recommandations

> Principe : **aucune IA opaque ne remplace le moteur déterministe**. Chaque recommandation est
> traçable à une règle et à des données réelles.

## Chaque `RecommendationItem` expose
- `type` : catégorie (weapon/talent/character_upgrade/team/rotation/data_quality…).
- `title` : nom court actionnable.
- `explanation` : la raison, en langage clair.
- `evidence[]` : **faits du scan** (niveau, arme, gaps réels) — jamais une opinion.
- `tradeoffs[]` : coûts/compromis explicites (ressources, priorisation).
- `expectedImpact` : **qualitatif** (jamais un « +X % DPS » fabriqué).
- `confidence` : haute/moyenne/faible, dérivée de la complétude des données.
- `requiredData[]` : ce qu'il faut compléter pour aller plus loin.

## Pourquoi pas de chiffre d'impact ?
Un « +12 % de DPS » exigerait de simuler l'avant/après build dans une rotation complète contre une
cible fixe. Tant que le moteur ne le calcule pas, afficher un tel chiffre serait **inventé**. Le
moteur dit donc « améliore la fiabilité du calcul » (vrai et vérifiable) plutôt qu'un faux gain.

## Passerelle vers le chiffré
Quand un build devient complet, l'utilisateur peut définir une rotation (`/rotations`) et comparer
deux équipes (`/team-compare`, `team-compare/1.0`) pour obtenir un DPS **réel** — la recommandation
pointe vers ces outils plutôt que de deviner.
