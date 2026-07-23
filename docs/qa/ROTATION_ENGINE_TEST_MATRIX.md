# Matrice de tests — moteur de rotations (`rotation/1.0`)

> Guidance skill : `senior-qa` (verified_read_only).

## Unitaires moteur (Python — `tests/test_rotation.py`, 13)
| Cas | Couvert | Résultat attendu |
|---|:--:|---|
| rotation vide | ✅ | `RotationValidationError` |
| équipe vide | ✅ | `RotationValidationError` |
| timestamp négatif | ✅ | rejeté |
| durée négative | ✅ | rejeté |
| acteur hors équipe | ✅ | rejeté |
| chevauchement | ✅ | rejeté |
| type inconnu | ✅ | rejeté |
| NaN/Infinity | ✅ | rejeté |
| rotation complète → DPS | ✅ | `average_damage_per_second = total/durée` |
| incomplète → pas de DPS | ✅ | `average_damage_per_second = None` |
| coefficient introuvable | ✅ | action incomplète + warning |
| swap/wait | ✅ | durée sans dégât |
| provenance/hypothèses | ✅ | présentes |

## Unitaires contrat (TS — `rotation.test.ts`, 6)
validation pure (vide/négatifs/NaN/acteur/chevauchement/valide) + adapter (mapping, DPS null si incomplet).

## Intégration
| Chaîne | Couvert |
|---|:--:|
| compte réel → stats finales (charstats) | ✅ (via sidecar character_final_stats, tranche précédente) |
| stats + coefficients → rotation | ✅ (rotation.py réutilise charstats/talentstats/damage) |
| sidecar `calculate_rotation` (protocole JSON) | ✅ (smoke bout-en-bout) |
| Server Action → UI | ✅ (E2E) |

## E2E (`team-lab.spec.ts` — 2 tests rotations)
créer équipe (Bennett) → /rotations → ajouter action → calculer → contrat visible, pas de NaN/Infinity,
hypothèses/provenance ; axe 0 critique/sérieux.

## Non couvert v1 (backlog, documenté)
timeout sidecar sous charge, multi-cible, énergie/cooldown chiffrés, buffs/réactions par action.
