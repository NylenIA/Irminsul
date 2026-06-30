# Revue de code Team Lab — cross-review Duo (Codex audite, Claude tranche)

> Mission Codex **read-only** (`codex exec --sandbox read-only`) sur `TeamLabClient.tsx` + `actions.ts` +
> `team-repository.ts`. Aucun fichier modifié par Codex. Claude relit chaque finding et décide.
> Sorties brutes : `.duo/runtime/codex-audit-teamlab.md`, `codex-review-team-repository.json` (gitignoré).

## Findings & décisions
| # | Sévérité (Codex) | Zone | Décision Claude | Action |
|---|---|---|---|---|
| 1 | Medium | `TeamLabClient` filtre retire l'option sélectionnée | **Déjà corrigé** | options incluent toujours `c.name === s.character` |
| 2 | Medium | Suppression sans confirmation | **Corrigé ce tour** | `ConfirmDialog` (native `<dialog>`, focus trap + Échap) |
| 3 | Low | Boutons « Supprimer » homonymes, pas de nom accessible distinct | **Accepté + corrigé** | `aria-label="Supprimer <équipe>"` (idem renommer/dupliquer) |
| 4 | Medium | `save` non idempotent (appels concurrents → doublons) | **Accepté, différé** | faible risque (app locale mono-utilisateur) ; clé d'op à ajouter plus tard |
| 5 | Medium | Pas de validation roster/`carry ∈ members` côté serveur | **Accepté partiel** | repo valide nom/1–4/slots/persos/anti-doublon ; appartenance roster = TODO |
| 6 | Medium | Persistance par **nom** et non `c.id` | **Accepté, différé** | les noms Genshin sont stables ; identité d'équipe = cuid DB (stable) |
| 7 | Low | Pas de `<form>` (Entrée ne soumet pas) | **Différé** | amélioration ergonomie clavier (non bloquant) |
| 8 | — | Frontière serveur/client | **Validé par Codex** | Prisma derrière `"use server"`, DTO en `import type` (aucune fuite client) |

## Bilan
Codex a confirmé l'architecture (frontière serveur/client saine) et identifié 7 améliorations. Les 2 plus
importantes (option sélectionnée, confirmation de suppression) étaient déjà traitées ; le finding a11y (#3)
a été intégré. Les findings 4–7 sont acceptés mais différés avec justification (non bloquants pour un produit
local-first mono-utilisateur). Aucune intégration aveugle.
