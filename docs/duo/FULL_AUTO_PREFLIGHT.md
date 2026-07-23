# Préflight Duo full-auto — état réel vérifié (2026-06-30)

> Tout ci-dessous = sortie de commandes exécutées. Les « coches » du prompt §12.1 sont **corrigées par la preuve disque**.

## Agents / CLI
| Outil | État réel | Détail |
|---|---|---|
| Claude Code | ✅ 2.1.195 | présent |
| **Codex CLI** | ❌ **ABSENT** | `which codex` = rien ; pas en PATH ni npm global. Installable (`@openai/codex` npm 0.142.4) **mais auth OpenAI interactive requise**. |
| Duo | ✅ `duo-agents 0.2.0` | `~/AppData/Roaming/npm/duo`. Sous-commandes réelles : `run/chat/send/watch/ui/status/accounts/agents/sessions/limits/pause/resume/scheduler/init/doctor/demo full-auto`. |
| duo-agents-fork | ✅ présent | `main`, **sans remote origin** ; JS (`src/dashboard.mjs`, `src/lib/event-store.mjs`, `src/lib/reliable-messages.mjs`). Pas de `supervisor.py`. |

## MCP (claude mcp list)
- `irminsul` — ⏸ Pending approval. `next-devtools` — ⏸ Pending approval. (+ serveurs cloud du compte : Gmail/Canva/Adobe/Claude Code Remote.)

## Skills (preuve disque) — voir `docs/skills/SKILL_EFFECTIVENESS.md`
- Installés et détectés : **frontend-design, skill-creator, webapp-testing** (3).
- **ABSENTS (15)** : senior-architect, senior-backend, senior-security, senior-frontend, senior-qa, code-reviewer, tdd-guide, ui-ux-pro-max, frontend-design-review, design, design-system, ui-styling, brand, banner-design, slides. (`ui-ux-pro-max-cli@2.9.0` est en npm global mais **aucun skill** correspondant n'est installé.)

## Conséquences (sans fabrication)
1. **Codex absent → IMPOSSIBLE** : collaboration Claude↔Codex, `codex exec` en worktree, cross-review, **tests A à H**, « full auto ». Ne sera **pas** déclaré. Déblocage = **Action utilisateur unique** (installer + `codex login`).
2. **15/16 skills absents → IMPOSSIBLE** de « qualifier les 16 skills » / « Claude détecte 16 skills ». Le registre reflète la réalité (3 installés). Déblocage = installer les skills réels (sources à résoudre/vérifier, pas inventer).
3. **Duo 0.2.0 existe** mais son mode collaboratif dépend de Codex → idem bloqué côté Codex. `duo doctor`/`duo status` exécutables en lecture, mais pas une vraie mission Claude↔Codex.

## Secrets
Aucun secret écrit. `codex login status` non exécutable (CLI absent).
