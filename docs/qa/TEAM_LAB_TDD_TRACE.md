# Trace TDD — Team Lab

> Preuve RED → GREEN → REFACTOR pour les règles non triviales. Tests : `packages/data-access/tests/team-repository.test.ts`.

## Règle : un personnage ne peut pas occuper deux emplacements
- **RED** : cas ajouté dans « rejects invalid input » — deux membres `character: "Sandrone"` (slots 0 et 1) → attendu `TeamRepositoryValidationError`. Sans implémentation, `save()` persiste les doublons → test rouge.
- **GREEN** : `validateSaveTeamInput` — `usedCharacters: Set<string>`, lève l'erreur si un personnage est déjà vu.
- **REFACTOR** : exclusion des doublons aussi côté UI (`takenElsewhere` filtre les options déjà choisies) — l'utilisateur ne peut plus tomber dans le cas d'erreur. Test toujours vert (garde serveur conservée).

## Comportement : renommage
- **RED** : `rename(id, "   ")` et `rename("missing-id", "X")` → attendus `TeamRepositoryValidationError`. Sans méthode → rouge.
- **GREEN** : `rename()` valide l'id + le nom (trim non vide) + existence avant `update`.
- **REFACTOR** : édition inline accessible côté UI (`aria-label`, Valider/Annuler) ; logique de validation centralisée (réutilise `validateTeamId`).

## Comportement : duplication
- **RED** : `duplicate("missing-id")` → erreur ; `duplicate(id)` → nouvelle équipe `"<nom> (copie)"`, membres identiques, id différent.
- **GREEN** : `duplicate()` relit la source puis **réutilise `save()`** (donc toute la validation s'applique à la copie).
- **REFACTOR** : bouton « Dupliquer » par équipe ; aucune duplication de logique de validation.

## Couverture
5 tests repository (Vitest) verts : CRUD, normalisation, rejets (nom/membres/slots/anti-doublon), idempotence delete, rename+duplicate. + E2E Playwright du workflow complet.
