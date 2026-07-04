# Triage — audit Codex read-only du moteur de rotations (`rotation.py`)

> Reçu : `.duo/runtime/codex-audit-rotation.md` (gpt-5.4-mini, worktree isolé — non détourné).
> Arrivé tardivement (après les gates) : triage + correctifs de suivi, politique reçus-tardifs.

| # | Sévérité | Finding | Décision | Correction / Test |
|---|---|---|---|---|
| 1 | **High** | `_cell()` vérifiait `value` finie mais **pas `complete`** → un build partiel (arme non supportée, main-stat non calculée) à valeurs finies pouvait produire un **DPS marqué complet** = faux chiffre. | **accepted + fixed** | nouveau `_complete_cell()` : l'ATQ n'est consommée que si `complete=true` ; sinon action incomplète + warning. Test `test_atk_incomplete_ne_produit_pas_de_faux_dps`. **Effet réel** : Bennett (ATQ incomplète dans le scan) ne produit plus de DPS — tests migrés sur Mavuika (ATQ complète). |
| 2 | **High** | `enemy` transmis à la formule sans validation → résistance non finie ⇒ NaN dans total/DPS ; niveau très négatif ⇒ `ZeroDivisionError` (dénominateur de défense) ; chaîne non numérique ⇒ crash. | **accepted + fixed** | `_validate_enemy()` : `level` ∈ [1,200], `resistance` ∈ [-1,3], finis, avant tout calcul. Tests `test_enemy_resistance_nan_rejete`, `test_enemy_level_hors_bornes_rejete`. |
| 3 | **Medium** | `actions=[None]` → `AttributeError` ; `team=[1]` stringifié en `"1"` laissait passer un acteur `"1"`. | **accepted + fixed** | chaque action doit être un `dict` ; membres d'équipe strictement chaînes non vides (pas de coercition). Tests `test_action_none_rejetee`, `test_membre_equipe_non_chaine_rejete`. |

## Vérifications positives de l'audit (confirmées)
- Coefficient absent/non-dégât → action incomplète (pas de dégât fabriqué).
- Checks de timeline (vide, négatifs, non-finis, overlap, MAX_ACTIONS) solides ; `durée=0` → pas de DPS.
- Aucune fuite de chemin local, aucune boucle non bornée.

## Gates post-correctif
pytest **217 passed** (+5 régression) · vitest **55** · build+TS PASS · E2E **28/28**.

**Verdict après correctifs : les 2 High et le Medium sont résolus → moteur conforme au contrat
« zéro chiffre inventé ».** Note : le durcissement damage.py (dénominateur ≤ 0) reste un follow-up
possible, mais la validation d'entrée `_validate_enemy` ferme le risque côté rotation.
