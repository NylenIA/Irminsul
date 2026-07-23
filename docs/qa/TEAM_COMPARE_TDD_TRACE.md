# Trace TDD — comparateur quantitatif (`team-compare/1.0`)

> `tdd-guide` : RED → GREEN → REFACTOR. Tests : `packages/engine-client/tests/team-compare.test.ts` (5).

| Règle | Test | GREEN |
|---|---|---|
| Deux rotations complètes → verdict + écart relatif | `deux rotations complètes → verdict` | ✅ (16.7 % calculé) |
| Une incomplète → **aucun verdict** quantitatif | `une rotation incomplète → AUCUN verdict` | ✅ (`complete=false`, DPS non comparable) |
| DPS égal → équivalence (pas de faux gagnant) | `DPS égal → verdict d'équivalence` | ✅ (`winner=tie`) |
| Durée : plus court = mieux | `durée : plus court = mieux` | ✅ |
| Même cible explicite, pas de méta globale | `hypothèses` | ✅ |

**Intégration** : Server Action lance `calculate_rotation` ×2 avec la MÊME cible ; E2E crée 2 équipes,
définit une action chacune, compare (28/28). **REFACTOR** : helper `diff()` paramétré `higherIsBetter`,
`summary()` extrait de `RotationResult`.
