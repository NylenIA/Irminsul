# Quarantaine des skills — politique et rationale

## Pourquoi
Le **28→30 juin**, un skill `code-reviewer` **non suivi** (présent dans `.agents/skills/` et
`.claude/skills/`, jamais committé) a **détourné une mission Codex read-only** : Codex a auto-chargé
ses fichiers de règles (`universal.md`, `typescript.md`) et suivi *son* workflow de génération de
rapport au lieu du prompt d'audit ciblé. Le reçu attendu a mis longtemps à arriver.

Enseignement : **un skill non vérifié ne doit jamais participer à une mission Codex.**

## Règle
| Statut | Critère | Portée |
|---|---|---|
| `verified_allowed` | **tracé par git** (committé = revu, versionné, diffable) | Claude **et** Codex |
| `quarantined` | **untracked** (`git status ??`) — source/auteur/licence/hash non prouvés | Claude en **lecture de référence** seulement ; **interdit** au routage Codex |

## Skills en quarantaine (untracked)
`code-reviewer`, `senior-architect`, `senior-backend`, `senior-frontend`, `senior-qa`,
`senior-security`, `tdd-guide`, `design`, `design-system`, `ui-styling`, `ui-ux-pro-max`,
`frontend-design-review`, `brand`, `banner-design`, `slides`.

**Risque élevé** (scripts Python exécutables auto-chargés par Codex) : `code-reviewer` (6),
`senior-architect` (6), `senior-backend` (8), `senior-frontend` (8), `senior-qa` (6),
`senior-security` (4). Les autres sont markdown-only (risque de détournement de contexte, pas d'exécution).

## Mitigations en place
1. **Worktree d'intégration neuf** (`irminsul-final-stats-worktree`) : un worktree n'hérite **pas**
   des fichiers untracked → `.agents/`, `.claude/skills/<untracked>` y sont **absents** → Codex n'y
   est pas détournable. Toutes les missions Codex de cette session tournent dans ce worktree. Vérifié.
2. **Aucun skill untracked n'est committé** (règle permanente respectée).
3. **Allowlist** (`VERIFIED_SKILL_ALLOWLIST.json`) : seule référence pour autoriser un skill.

## Sortie de quarantaine (procédure)
Pour promouvoir un skill en `verified_allowed` : (1) identifier sa source/auteur/licence/commit,
(2) auditer ses scripts, (3) figer un SHA-256, (4) le committer explicitement. Tant que ce n'est pas
fait, ses *principes* markdown peuvent inspirer Claude, mais son code ne s'exécute pas et il ne route
aucune mission Codex.
