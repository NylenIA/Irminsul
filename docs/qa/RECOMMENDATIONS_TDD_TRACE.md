# Trace TDD — recommandations (`recommendations/1.0`)

> `tdd-guide` : RED → GREEN → REFACTOR. Tests : `packages/engine-client/tests/recommendations.test.ts` (6).

| Règle | Test | GREEN |
|---|---|---|
| Build incomplet signalé avec preuves réelles | `data_quality` | ✅ (evidence = arme manquante) |
| Jamais de personnage non possédé ; exclusions respectées | `ne recommande JAMAIS un non possédé` | ✅ |
| Goulot d'étranglement = build le plus incomplet | `improve_current_team` | ✅ (Weak identifié) |
| Classement par complétude réelle des membres | `highest_complete_dps` | ✅ (Full 2/2 haute, Partial 1/2 moyenne) |
| Objectif non modélisé → qualitatif + missingData | `objectif non modélisé` | ✅ (`non quantifié`, `low`) |
| Scan vide → missingData explicite | `aucun personnage possédé` | ✅ |

**Méthode** : éliminer l'invalide → complétude → prouvable → goulots → explication. Aucun impact
chiffré inventé. **Intégration** : Server Action résout builds+équipes réels côté serveur ; E2E
(qualité des données + objectif non modélisé + axe).
