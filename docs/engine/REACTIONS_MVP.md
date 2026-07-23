# Réactions élémentaires — MVP (contrat `reactions/1.0`)

> Source unique : `src/irminsul/reaction.py` (formules **KQM**, niveau 90 = 1446.85).
> Parité TS prouvée : goldens générés du moteur réel (`scripts/gen-reaction-goldens.py`,
> 5 amplifiantes + 10 transformatives, tolérance 1e-9) + garde pytest inverse
> (`tests/test_reaction_goldens_guard.py`) — le moteur ne peut pas dériver silencieusement.

## Implémenté (v1)
| Catégorie | Réactions | Formule | Confiance |
|---|---|---|---|
| **Amplifiantes** (multiplient le coup) | forward/reverse-vaporize, forward/reverse-melt | `base × (1 + 2.78·EM/(EM+1400) + bonus)` ; base 2.0 / 1.5 | haute (verified) |
| **Transformatives** (dégâts propres, sans crit) | swirl, superconduct, electro-charged, overloaded, shattered, burning, bloom, hyperbloom, burgeon | `base × 1446.85 × (1 + 16·EM/(EM+2000) + bonus) × RES` | haute (verified) |

## Hors périmètre v1 (affiché dans les hypothèses UI)
- **Additives** (Aggravation/Propagation) : implémentées dans le moteur **phase3** non fusionné → pas de port sans source sur cette branche.
- **Cristallisation** (bouclier, pas de dégâts) : utilitaire, non modélisée v1.
- Uptime d'aura, ICD, direction implicite : jamais devinés (gcsim pour les rotations).

## UI (Team Lab → Aperçu de coup direct)
Sélecteur groupé (amplifiantes/transformatives) + champ Maîtrise élémentaire. Amplifiante :
badge `×multiplicateur` + dégâts du coup multipliés. Transformative : sous-carte dédiée
(dégâts propres). Hypothèses des réactions ajoutées au dépliant provenance. Cas limites
testés : EM 0, RES 0 et 0.75, bonus négatif clampé, niveau ≠ 90, réaction inconnue rejetée.
