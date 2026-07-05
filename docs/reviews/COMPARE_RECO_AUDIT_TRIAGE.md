# Triage — audit Codex read-only du comparateur quantitatif + recommandations

> Reçu : `.duo/runtime/codex-audit-compare-reco.md` (gpt-5.4-mini, worktree isolé — non détourné).
> Arrivé tardivement (après gates) : triage + correctifs de suivi (politique reçus-tardifs).

| # | Sévérité | Finding | Décision | Correction / Test |
|---|---|---|---|---|
| 1 | **Medium** | Exclusions appliquées **seulement** dans la branche `data_quality` ; `highest_complete_dps` et `improve_current_team` raisonnaient sur tous les membres → un perso exclu pouvait être recommandé, un membre non possédé devenir « goulot ». | **accepted + fixed** | ensemble `allowed = possédés − exclus` utilisé dans **toutes** les branches ; membres non autorisés signalés en `missingData`, jamais en goulot améliorable. 2 tests |
| 2 | **Medium** | `repo.getById()` hors `try/catch` dans `compare-actions` → `teamId` malformé ⇒ `TeamRepositoryValidationError` non typée (500) au lieu de `{ok:false}`. | **accepted + fixed** | validation `teamId.trim()` avant appel + `try/catch` mappant vers `validation_error` ; bonus : `count` validé (1..20). |
| 3 | **Low** | `diff()` calculait `winner`/`relativePct` sans regarder `complete` → une rotation incomplète à valeurs finies pouvait produire un gagnant de métrique (le verdict global était déjà bloqué). | **accepted + fixed** | si `!bothComplete`, **toutes** les métriques forcées `computable:false`, `winner:null`, `relativePct:null`. 1 test |

## Vérifications positives de l'audit (confirmées)
- Chemin UI sain : pas de division par zéro/NaN dans `relativePct` ; **même cible** passée aux deux rotations.
- Pas de fuite de `source_path`/blob brut vers l'UI (provenance = `source` du profil).
- Cas limites couverts : `teamId` identique rejeté, équipe introuvable gérée, rotations vides rejetées.
- Réserve notée : `target.count` était décoratif → désormais **validé** (1..20) ; usage multi-cible reste une tranche future (documenté dans les hypothèses).

## Gates post-correctif
vitest engine-client **69** (+3 régression) · build+TS PASS · E2E **34/34** · axe vert.

**Verdict après correctifs : les 2 Medium et le Low sont résolus.**
