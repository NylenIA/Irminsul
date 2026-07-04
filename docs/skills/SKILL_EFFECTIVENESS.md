# Registre d'efficacité réelle des skills (mis à jour 2026-07-04)

> Un skill n'est « utilisé » que s'il **influence un fichier, une revue, un test ou une décision**.
> Les scripts des skills en quarantaine **ne sont pas exécutés** (audit statique seulement —
> `SKILL_AUDIT_MATRIX.md`). Détail machine : `SKILL_EFFECTIVENESS.json`.
> Provenance revendiquée des untracked (non confirmée) : `alirezarezvani` (senior-*/code-reviewer/
> tdd-guide) + divers npm (design*/ui-*/brand/slides). Aucune source figée → restent en quarantaine.

## Skills tracés (verified_allowed)
| Skill | Mission réelle cette session | Fichiers | État |
|---|---|---|---|
| webapp-testing | E2E Playwright des parcours (rotations inclus) | `apps/web/tests/e2e/team-lab.spec.ts` | qualifying |
| genshin-* (domaine) | vocabulaire mécaniques/vérif | docs moteur | candidate |
| skill-creator | (skill interne rotation à formaliser) | — | candidate |

## Skills en quarantaine — guidance appliquée à des livrables RÉELS (scripts NON exécutés)
| Skill | Verdict | Livrable influencé cette session |
|---|---|---|
| senior-architect | verified_read_only | [ROTATION_ENGINE_ADR.md](../architecture/ROTATION_ENGINE_ADR.md) |
| senior-backend | verified_claude_only | `src/irminsul/rotation.py` (contrats, erreurs typées, bornes) |
| senior-security | verified_read_only | bornes MAX_ACTIONS/MAX_TIME, gardes NaN/inf, messages sans chemin |
| senior-qa | verified_read_only | [ROTATION_ENGINE_TEST_MATRIX.md](../qa/ROTATION_ENGINE_TEST_MATRIX.md) |
| tdd-guide | verified_read_only | [ROTATION_TDD_TRACE.md](../qa/ROTATION_TDD_TRACE.md), tests RED→GREEN |
| senior-frontend | verified_read_only | `apps/web/src/app/rotations/` |
| design-system | verified_read_only | `.irm-table`, badges, halo |
| ui-styling | verified_read_only | focus-visible, reduced-motion, densité éditeur |
| ui-ux-pro-max | verified_read_only | hiérarchie /rotations (DPS mis en avant, warnings visibles) |
| frontend-design-review | verified_read_only | revue états idle/partial/error |
| design | verified_claude_only | cohérence Archive astrale (scripts Gemini NON exécutés) |
| code-reviewer | verified_claude_only | revue **déléguée à Codex isolé**, pas au skill (hijack évité) |
| brand / banner-design / slides | verified_read_only | backlog (non prioritaires cette tranche) |

## États de promotion
`candidate` → `qualifying` (1 mission réelle) → `qualified` (≥2 missions + revue croisée + gates
vertes + 0 régression) → `degraded` / `quarantined`.

**Honnêteté** : aucun skill n'est `qualified` par simple présence disque. Les skills en quarantaine
sont au mieux `qualifying` (guidance appliquée une fois) — leur code n'a pas tourné, leur provenance
`alirezarezvani`/npm reste **non confirmée**. Promotion en `verified_allowed` seulement après preuve
de source + audit scripts + commit explicite.
