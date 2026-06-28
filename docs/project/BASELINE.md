# BASELINE & rapport Phase 0 — efficacité des tokens

Mesures déterministes via `python scripts/measure_context.py` (estimation ~chars/4).
Données brutes : `.irminsul/index/baseline.json` (avant) et `.irminsul/index/after.json` (après).

## Contexte permanent (toujours chargé)
| Élément | Avant | Après |
|---|---|---|
| **PERMANENT tokens_est** | **1678** | **1434** (−15 %) |
| CLAUDE.md (lignes / tok) | 89 / 1144 | 49 / 900 |
| MEMORY.md (index) | 10 / 242 | 10 / 242 |
| orchestrateur (agent) | 16 / 292 | 16 / 292 |
| Règles par chemin | 0 | 2 (`dps`, `account`, chargées au besoin) |

## Scénarios de référence (avant/après)
| Scénario | Avant | Après | Réduction |
|---|---|---|---|
| Sortie d'outil (pytest -v) → résumé `run_logged` | 7498 o | 336 o | **96 %** (cible ≥ 70 %) |
| GOOD complet → projection `peek_json` | 166 134 o | 1 935 o | **99 %** (cible ≥ 50 %) |
| GOOD envoyé au modèle | (jamais) | (jamais) | garanti |

Le code de sortie réel et les erreurs uniques sont **toujours préservés** (vérifié : exit 0 et exit 3 propagés).

## Porte de passage Phase 0 — état
- [x] Baseline enregistrée + script reproductible
- [x] CLAUDE.md réduit/dédupliqué (49 < 200) ; leaks/sources/DPS dédoublonnés (→ `RESEARCH_POLICY`, `.claude/rules/`)
- [x] Règles spécialisées → `.claude/rules/{dps,account}.md` (frontmatter `paths`) + skills à la demande
- [x] Lectures ciblées + index léger : `scripts/index_repo.py`, skill `project-context`
- [x] Sorties tests/logs compressées sans masquer les erreurs : `scripts/run_logged.py` (−96 %, exit code + erreurs)
- [x] MCP/skills/sous-agents audités : 1 serveur MCP, skills/agents chargés à la demande (coût permanent nul) ; cf. `DECISIONS.md`
- [x] Politique adaptative modèles/effort : `config/token-budgets.json` (`model_routing`) + `CLAUDE.md`
- [x] Gros fichiers/GOOD/SQLite/gcsim exclus du contexte : `peek_json.py` + `never_inline_full` + règle `account`
- [x] Budgets souples + groupes d'outils + cache documentés (`token-budgets.json`, `DECISIONS.md`) ; prompt caching **préparé** (préfixe stable tools→system→messages), finalisé en Phase 5
- [x] Fichiers de reprise : `docs/project/*` + skill `session-handoff`
- [x] Scénarios mesurés avant/après (ci-dessus)
- [x] Tests de non-régression de l'infra : `tests/test_phase0_infra.py` (suite : **83 passed**, Ruff OK)
- [x] Rapport (ce fichier) + commit stable

**Garanties non négociées** : aucun résultat validé modifié (83 tests verts), aucun test réduit, aucun secret/GOOD versionné, aucune source omise.

**Porte : OUVERTE** → passage en Phase 1 autorisé.
