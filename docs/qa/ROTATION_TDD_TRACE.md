# Trace TDD — moteur de rotations (RED → GREEN → REFACTOR)

> Guidance skill : `tdd-guide` (verified_read_only). Tests écrits pour cadrer le comportement,
> puis implémentation, puis durcissement.

## Règles fondamentales couvertes (`tests/test_rotation.py`, 13 tests)
| Règle | Test | RED attendu | GREEN |
|---|---|---|---|
| Rotation vide interdite | `test_rotation_vide_rejetee` | `RotationValidationError` | ✅ |
| Équipe vide interdite | `test_equipe_vide_rejetee` | idem | ✅ |
| Timestamp négatif interdit | `test_timestamp_negatif_rejete` | idem | ✅ |
| Durée négative interdite | `test_duree_negative_rejetee` | idem | ✅ |
| Acteur hors équipe | `test_acteur_hors_equipe_rejete` | idem | ✅ |
| Chevauchement interdit | `test_chevauchement_rejete` | idem | ✅ |
| Type d'action inconnu | `test_type_inconnu_rejete` | idem | ✅ |
| NaN/Infinity rejetés | `test_nan_infinity_rejetes` | idem | ✅ |
| Rotation complète → DPS | `test_rotation_complete_produit_dps` | DPS = total/durée | ✅ |
| **Incomplet → PAS de DPS** | `test_action_sans_talent_est_incomplete_sans_faux_dps` | `average_damage_per_second is None` | ✅ |
| Coefficient introuvable → incomplet | `test_coefficient_introuvable_incomplet` | warning, pas de dégât | ✅ |
| swap/wait = durée sans dégât | `test_swap_et_wait_comptent_la_duree_sans_degats` | dégât None | ✅ |
| Provenance/hypothèses présentes | `test_provenance_et_hypotheses_presentes` | talent_source rempli | ✅ |

## Côté TS (`packages/engine-client/tests/rotation.test.ts`, 6 tests)
Validation pure (vide, négatifs, NaN, acteur hors équipe, chevauchement, valide) + adapter
(mapping camelCase, DPS/total `null` si incomplet).

## REFACTOR appliqué
Extraction de `_compute_action_damage` / `_cell` / `_finite` ; helpers `_level_or` réutilisés du
durcissement précédent ; bornes `MAX_ACTIONS`/`MAX_TIME` centralisées.
