# Triage — audit Codex read-only des Tranches B (stats réelles/sidecar) et C (réactions)

> Audit : `codex exec` read-only (gpt-5.4-mini). Sortie brute : `.duo/runtime/codex-audit-b-c.md`
> (gitignoré). Chaque finding tranché par Fable, corrections testées.

| # | Sévérité | Finding | Décision | Correction / Test |
|---|---|---|---|---|
| 1 | Moyenne | Réponse sidecar castée sans validation (`exitCode`/`engine`/schéma) → un payload malformé pouvait sortir « python-sidecar » avec des valeurs fausses | **accepted + fixed** | `runSidecar` : rejet si `engine ≠ python-sidecar` ou `result` non-objet (+ exit code dans les erreurs) ; `calculateDirectHit` : 7 champs numériques validés `Number.isFinite` sinon `SidecarError` |
| 2 | Moyenne | Alias Python `overload`/`shatter` absents du port TS → réactions valides rejetées | **accepted + fixed** | `TRANSFORMATIVE_LOOKUP` (canoniques + alias) + helpers `isTransformativeKind`/`isAmplifyingKind` utilisés par preview ; **2 goldens alias ajoutés** (17 goldens réactions), parité verte |
| 3 | Faible | `Math.round` ≠ `round()` Python (ties-to-even) sur les champs arrondis | **deferred (justifié)** | Aucun cas de tie démontré ; les goldens à 1e-9 échoueraient bruyamment sur un tie réel → on implémentera ties-to-even au premier golden rouge. Documenté ici. |

## Vérifications positives de l'audit (design confirmé)
- Aucune fuite du scan : `build-actions` ne renvoie que le DTO du perso demandé.
- Frontière client/serveur saine : `node:child_process` derrière `use server`, hors barrel.
- Sidecar sans vecteur d'injection : `shell:false`, `windowsHide:true`, stdin JSON, timeout ; one-shot sans enfants → risque orphelin faible.
- Clamps EM/bonus/RES conformes au moteur.

## Gates après triage
vitest engine-client **43/43** · gardes pytest **2/2** · build + TypeScript **PASS**.
