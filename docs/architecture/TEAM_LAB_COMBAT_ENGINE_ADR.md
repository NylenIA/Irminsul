# ADR — Frontière Team Lab ↔ moteur de combat

> Statut : **accepté** (2026-07-01) · Pilote du routeur Duo (mission classifiée `architecture/complex` →
> Claude fable/high + délégation Codex). Décision produit verrouillée : local-first (D-LF1).

## Contexte
- Le **moteur de référence** est Python (`src/irminsul/` : damage, reaction, quickcalc, charstats…),
  **20 modules, 96 tests, goldens vérifiés en jeu**, registre de mécaniques versionné. Il est accessible
  au desktop via le sidecar Tauri (stdin/stdout borné) — mais **pas** à l'app web (`apps/web`).
- Le Team Lab (Next.js) sauvegarde des équipes mais n'affiche **aucun calcul**. Interdit : afficher un
  « DPS » fabriqué ; obligatoire : provenance + hypothèses sur tout chiffre.

## Décision
1. **Une frontière unique : l'interface `EngineClient`** (`packages/engine-client/src/contract.ts`).
   L'UI (web et desktop) ne dépend que de ce contrat TypeScript — jamais d'une implémentation.
2. **Deux implémentations prévues** :
   - `LocalEngineClient` (**maintenant**) : portage TS *fidèle* des formules Python dont le statut
     registre est `verified` (d'abord `calculate_direct_hit`). **Parité prouvée par goldens générés
     depuis le moteur Python réel** (`scripts/gen-engine-goldens.py` → tolérance 1e-9). Le moteur
     Python reste la **source de vérité** ; tout ajout TS exige de nouveaux goldens.
   - `SidecarEngineClient` (**desktop, plus tard**) : délègue au sidecar Python via Tauri — même contrat.
3. **Chaque résultat porte sa provenance** (`engine`, `formula`, `registryStatus`, `assumptions`).
   L'UI doit afficher les hypothèses (« coup isolé, pas un DPS d'équipe — gcsim pour cela »).
4. **Périmètre v1** : coup direct (non-crit / crit / attendu, DEF, RES, amplification explicite).
   Réactions additives/transformatives, énergie, rotations = extensions ultérieures, chacune goldens-first.

## Alternatives rejetées
- **Spawner Python depuis Next.js** : exige Python chez l'utilisateur web, fragile Windows, contredit
  la distribution sidecar. Rejeté.
- **Réécrire le moteur en TS comme source de vérité** : perd 96 tests + goldens en jeu + registre. Rejeté.
- **Afficher un score « maison » sans moteur** : donnée inventée. Interdit par la politique du projet.

## Conséquences
- Le Team Lab peut afficher un **premier calcul déterministe honnête** (par membre, coup isolé) sans cloud.
- Risque contrôlé : **dérive de parité** TS↔Python → mitigé par goldens régénérables et CI ; toute
  divergence > 1e-9 casse les tests.
- La formule TS ne doit jamais évoluer sans évolution correspondante du moteur Python (source de vérité).

## Preuves
- Contrat + implémentation : `packages/engine-client/` · Goldens : `tests/direct-hit.goldens.json`
  (générés, provenance en en-tête) · Tests : `direct-hit.golden.test.ts` (parité 1e-9, erreurs, provenance).
