# Méthode DPS

## Trois niveaux

### 1. Coup isolé

Le moteur local calcule : base de dégâts, bonus, réaction amplificatrice fournie, défense, résistance et espérance critique. Il sert à expliquer une formule ou vérifier une feuille.

Pour les réactions, deux helpers dédiés et transparents :

- `calculate_transformative_reaction` (ou `irminsul reaction transformative`) : dégâts d'une réaction transformative (Hyperbloom, Burgeon, Overload, Swirl, Superconduct, Bloom, Burning…), sans crit, avec bonus de Maîtrise selon la formule `16·EM/(EM+2000)`.
- `calculate_amplifying_multiplier` (ou `irminsul reaction amplifying`) : multiplicateur Vaporize/Melt avec bonus de Maîtrise `2.78·EM/(EM+1400)`, à injecter dans le coup amplifié.

Hypothèse par défaut : coefficient de niveau personnage 90 (`1446.85`). Fournir `level_multiplier` pour un autre niveau.

### 2. Rotation

Utiliser gcsim avec : builds exacts, constellation, raffinements, talents, ennemi, nombre de cibles, énergie initiale, génération de particules et rotation. Conserver le fichier de configuration dans `simulations/`.

### 3. Performance pratique

Ajuster le résultat selon : interruption, esquives, dispersion des ennemis, ping, erreurs de rotation, temps de setup, overkill et contenu. Ce niveau est une estimation, pas une simulation parfaite.

## Comparaison équitable

Deux équipes doivent partager :

- niveau d'investissement comparable ;
- même ennemi, durée et nombre de cibles ;
- même politique d'énergie ;
- mêmes buffs externes ;
- rotations réalistes ;
- mêmes hypothèses de constellations et armes.

## Rapport minimum

- DPS moyen et dispersion ;
- durée de rotation ;
- part de chaque personnage ;
- réactions ;
- énergie et risques de rupture ;
- frontload ;
- hypothèses ;
- limite de la simulation.
