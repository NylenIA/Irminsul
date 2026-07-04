# ADR — Moteur de rotations chiffrées (`rotation/1.0`)

- **Statut** : accepté et implémenté (tranche verticale MVP).
- **Guidance skill** : `senior-architect` (verified_read_only) — frontière moteur/UI, réutilisation
  des formules vérifiées.

## Décision
Le calcul de dégâts d'une rotation reste **en Python** (`src/irminsul/rotation.py`), réutilisant
les modules **déjà vérifiés** : `talentstats` (coefficients sourcés/versionnés), `charstats`
(stats finales réelles), `damage.calculate_direct_hit`. Exposé via le sidecar
(`calculate_rotation`). La couche **TS** possède le contrat `rotation/1.0`, la **validation de
timeline pure** (défense en profondeur, testable) et l'UI `/rotations`.

```
Actions (UI) → validateRotation (TS, pur) → Server Action → sidecar calculate_rotation
  → rotation.py:  pour chaque action de dégât →
       coefficient talent RÉEL × ATQ finale RÉELLE × calculate_direct_hit
  → agrégation (total, /perso, durée) → DPS SEULEMENT si complet
```

## Invariants (raison : honnêteté du chiffre)
- **Aucun coefficient inventé** : coefficient manquant/non-dégât → action `complete:false` + warning.
- **Aucune stat inventée** : ATQ finale indisponible → action incomplète.
- **Aucun faux DPS** : `average_damage_per_second` produit **uniquement** si toutes les actions de
  dégât sont complètes ET durée > 0. Sinon `null` + note « rotation incomplète ».
- **Bornes strictes** : timestamps/durées ≥ 0 et finis, pas de chevauchement, acteur ∈ équipe,
  ≤ 200 actions, ≤ 3600 s. NaN/Infinity rejetés avant le moteur.

## Périmètre v1 (tranche verticale)
Actions : normal/charged/plunging/skill/burst (dégât) + swap/wait (durée seule). Mono-fil,
séquence non chevauchante. **Hors périmètre v1** (documenté, non inventé) : buffs conditionnels,
réactions par action, énergie/recharge chiffrée, cooldowns, multi-cible — bonus de dégâts = 0
explicite. Ces axes viendront par tranches, chacun sourcé et testé.

## Alternatives rejetées
- **Réécriture TS des dégâts** : dupliquerait les formules → dérive de parité. Rejeté (Python = source).
- **DPS estimé quand incomplet** : violerait « jamais de faux chiffre ». Rejeté catégoriquement.

## Preuves
pytest `test_rotation.py` **13/13** · vitest `rotation.test.ts` **6/6** · sidecar validé bout-en-bout
(Bennett : action complète → dégâts réels ; label inexistant → incomplet, DPS null).
