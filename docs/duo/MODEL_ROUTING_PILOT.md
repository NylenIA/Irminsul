# Routage de modèles Duo — découverte réelle + plan pilote (Irminsul)

> Fondé sur les modèles **réellement découverts** (aucune invention). Catalogues compacts (métadonnées
> seules, sans les instructions système massives) : `.duo/runtime/model-catalog/` (gitignoré).

## Modèles réels découverts (2026-07-01)
### Claude Code 2.1.195
- Sélection : `claude --model <alias>` + `--fallback-model`. Alias confirmés dans `--help` : **fable, opus, sonnet**. Usuels non vérifiés runtime : haiku, opusplan, best.

### Codex (`codex debug models`)
| slug | rôle | efforts | visibilité |
|---|---|---|---|
| `gpt-5.5` | frontier (code/recherche complexe) | low/medium/high/xhigh | list |
| `gpt-5.4` | standard | low/medium/high/xhigh | list |
| `gpt-5.4-mini` | rapide/léger | low/medium/high/xhigh | list |
| `codex-auto-review` | revue automatique | low/medium/high/xhigh | hide |

## Profils (mappés sur les vrais modèles — à confirmer par benchmark, pas par défaut le plus puissant)
| Profil | Claude (préf.) | Codex (préf.) | Effort | Sandbox |
|---|---|---|---|---|
| trivial / fast | haiku (fb sonnet) | gpt-5.4-mini | low/minimal | read-only |
| routine / standard | sonnet (fb opus) | gpt-5.4 | medium | worktree-write |
| hybride | opusplan | gpt-5.4 | high | worktree-write |
| complex / deep | opus|best (fb opus) | gpt-5.5 | high/xhigh | adaptée |
| review | sonnet | gpt-5.4-mini / codex-auto-review | low | read-only |

## Délégation Codex obligatoire (Irminsul)
`delegationPolicy = required` · `minimumCodexTasks = 1` · grandes missions = ≥1 read-only + ≥1 worktree-write.
Exemptions tracées (`{"codexDelegation":"exempt","reason":"..."}`), jamais silencieuses.

## Statut honnête (ce qui est fait vs à faire)
- ✅ **Découverte réelle des modèles** (Claude + Codex), catalogues compacts.
- ✅ **Profils conçus sur données réelles** (ci-dessus).
- ⏳ **À implémenter (mission Codex worktree dans le fork Duo `feat/mandatory-delegation-model-router`)** :
  classifieur déterministe, résolution de profil au runtime, context packs minimaux, télémétrie
  (`.duo/runtime/telemetry/model-routing.jsonl`), fallbacks, overrides, tests Windows. **Non implémenté ce tour** —
  c'est une mission autonome longue ; je ne déclarerai ni routeur « fait » ni réduction de tokens chiffrée **sans mesure réelle** (baseline avant/après).
- ⏳ **Pilote** : ADR Team Lab ↔ moteur de combat + 1er contrat de calcul déterministe (sans faux DPS).

## Anti-fabrication
Aucun modèle inventé. Aucun pourcentage de réduction annoncé sans baseline+mesure. Pas d'intégration aveugle d'un diff Codex.
