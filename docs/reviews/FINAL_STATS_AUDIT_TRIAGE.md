# Triage — audit Codex read-only du portage stats finales (commit 4b9de45)

> Reçu : `.duo/runtime/codex-audit-finalstats.md` (gpt-5.4-mini, worktree isolé — non détourné).
> Reçu arrivé **tardivement** (après le merge+gates) : triage + correctifs de suivi appliqués,
> conformément à la politique reçus-tardifs (`pending-receipts.json`).

| # | Sévérité | Finding | Décision | Correction / Test |
|---|---|---|---|---|
| 1 | **Medium** | `artifact_stat_totals` : substat `value` absente/`None` → `0.0` silencieux ; artéfact sans `mainStatKey` → `continue` silencieux. Un artéfact corrompu disparaissait sans anomalie alors que `complete` pouvait rester `True`. | **accepted + fixed** | value `None` → anomalie « sans valeur » (jamais additionnée) ; mainStatKey absent → anomalie « sans stat principale ». 3 tests |
| 2 | **Medium** | `character_payload` : `level or 1` promouvait un niveau falsy réel (`0`) en niveau 1 → stats plausibles mais fausses, parfois marquées complètes. | **accepted + fixed** | helpers `_level_or`/`_ascension_or` : fallback **uniquement** pour `None`/non-entier ; `0` conservé → rejeté par les gardes de basestats (`supported:false`). 2 tests |
| 3 | **Low** | `load_basestats`/`load_weaponstats` : le message d'erreur données-absentes incluait le **chemin absolu local** → divulgation du layout via `character-stats`. | **accepted + fixed** | messages génériques (nom de fichier seul, pas de chemin/lettre de lecteur). 2 tests |

## Vérifications positives de l'audit (design confirmé)
- Chemin nominal : **aucune fuite** de `source_path` ni de payload brut du scan.
- Provenance présente et honnête (répartie `character/base_stats/weapon_base_stats/talents_detail`).
- `dispatch("character-stats")` : `params` validé objet par le sidecar avant appel.

## Gates post-correctif
`tests/test_charstats_audit_findings.py` **7/7** · pytest complet **199 passed** · smoke Mavuika
inchangé (`complete=True`, ATQ 2377.52) · build+TS PASS · E2E 20/20 · vitest 49/49.

**Verdict après correctifs : les 2 Medium et le Low sont résolus → portage validé comme output honnête.**
