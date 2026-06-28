---
description: Règles de calcul de dégâts / réactions / gcsim (chargées quand on touche ces modules)
paths:
  - "src/irminsul/damage.py"
  - "src/irminsul/reaction.py"
  - "src/irminsul/gcsim.py"
  - "src/irminsul/team_optimizer.py"
  - "tests/test_damage.py"
  - "tests/test_reaction.py"
  - "tests/test_team_optimizer.py"
---
# Calculs DPS / réactions

- Coup isolé → `calculate_direct_hit`. Équipe/rotation → privilégier `run_gcsim`.
- Ne compare jamais deux sims avec des standards d'investissement différents sans le signaler.
- Distingue : DPS théorique, réalisable, frontload, dégâts/rotation, AoE, énergie, interruption, temps mort.
- Jamais un chiffre unique sans plage/hypothèses/sensibilité quand l'incertitude est notable.
- Formules, constantes, ordre des opérations et arrondis : **versionnés, sourcés, testés** (KQM en référence).
- N'invente aucune interaction : une mécanique incertaine produit un **avertissement**, pas une fausse précision.
- `team_optimizer` = modèle analytique (plafond de buffs), **pas** un gcsim → valider le top via gcsim.

## Évaluation d'une équipe (minimum)
Monocible et multi-cible · rotation · recharge · interruption et soin · dépendance constellations/armes
limitées · compatibilité des deux côtés de l'Abîme · concurrence pour supports/artefacts · qualité réelle
des builds du joueur. Sépare toujours : DPS brut, praticité, méta théorique, méta pratique, popularité,
perf du compte réel. Un score de praticité ne modifie jamais silencieusement le DPS.
