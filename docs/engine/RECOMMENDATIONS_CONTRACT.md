# Contrat de recommandations — `recommendations/1.0`

> Moteur DÉTERMINISTE et EXPLICABLE, fondé **uniquement** sur les données réelles du compte
> (`PlayerCharacterBuild`) et les équipes sauvegardées. Guidance : `senior-architect`, `senior-qa`, `tdd-guide`.

## Interdictions (dures)
- Aucun classement arbitraire / score secret.
- Aucune donnée web non sourcée, aucun leak.
- Aucun personnage **non possédé** recommandé sans le signaler.
- Aucun **chiffre d'impact inventé** : `expectedImpact ∈ {qualitatif, améliore la fiabilité du calcul, non quantifié}`.
- Si les données ne permettent pas : « données insuffisantes / confiance faible / qualitatif uniquement ».

## Méthode explicable (ordre)
1. **Éliminer l'invalide** : seuls les personnages possédés et non exclus sont candidats.
2. **Évaluer la complétude** : `buildGaps()` = niveau/arme/artéfacts(<5)/talents manquants (champs réels du scan).
3. **Recommander le prouvable** selon l'objectif.
4. **Identifier les goulots** (membre au build le plus incomplet).
5. **Expliquer** : chaque item porte `evidence[]` (données réelles), `tradeoffs[]`, `requiredData[]`, `confidence`.

## Objectifs
| Objectif | Calcul honnête |
|---|---|
| `data_quality` | builds incomplets → recommandation d'amélioration (evidence = gaps réels) |
| `improve_current_team` | goulot d'étranglement de l'équipe (build le plus incomplet) |
| `highest_complete_dps` | équipes classées par **complétude réelle** des membres (n/total) |
| `balanced_team` / `low_investment` / `survivability` / `reaction_focus` | **qualitatif uniquement** + `missingData` (critères soin/bouclier/énergie non modélisés → pas de faux chiffre) |

## Confiance
Dérivée : `high` si toutes les recos sont `high` ; `medium` si mélange ; `low` sinon. Jamais gonflée.

## Provenance
Source + date d'import du scan (curées — jamais de chemin local).

## Tests (`recommendations.test.ts`, 6)
builds incomplets signalés, non-possédés jamais recommandés + exclusions, goulot d'étranglement,
classement par complétude, objectif non modélisé → qualitatif + missingData, scan vide → missingData.
