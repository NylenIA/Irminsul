# SKILLS_AUDIT — recherche, audit et décisions

> Politique : n'installer **aucun** skill opaque, non maintenu, surdimensionné, ou non vérifiable.
> Phase actuelle = **audit** (PR #3 mathématique en cours) → aucune installation qui ajoute une
> dépendance/contexte permanent avant la branche de refonte. Codex reste **read-only**.

## Contexte d'outillage (vérifié 2026-06-29)
- **`find-skills` : INDISPONIBLE** dans cet environnement (ni binaire sur le PATH, ni plugin sous
  `~/.claude/plugins`). → la découverte automatique demandée n'est pas exécutable ; recherche faite via le site.
- **skills.sh** : installation `npx skills add <owner/repo>`. **Le répertoire n'affiche NI licence NI URL
  de dépôt par skill** (seulement org/skill). → impossible de satisfaire les règles d'audit 1/3/4/6
  (inspecter dépôt, scripts, dépendances, licence) sans cloner/inspecter chaque dépôt manuellement.
- **Skills locaux déjà installés** : `.claude/skills/genshin-*` (≈30, propres au domaine Irminsul) — pas de
  skill UI/sécurité/revue de code. Aucun doublon avec les candidats ci-dessous.

## Évaluation des candidats (par domaine demandé)

| Skill candidat | Source | Licence | Rôle | Risques | Décision | Justification |
|---|---|---|---|---|---|---|
| `frontend-design` | anthropics/skills | (Anthropic, à confirmer) | guides design UI agents | faibles (org officielle) | **deferred-to-vet** | candidat le + fiable (même org que Claude Code) ; lire `SKILL.md`+scripts avant install |
| `web-design-guidelines`, `vercel-react-best-practices`, `vercel-composition-patterns` | vercel-labs/agent-skills | à vérifier | bonnes pratiques React/design | faibles-moyens (org réputée) | **deferred-to-vet** | utile pour la refonte React ; vérifier scripts/permissions |
| `shadcn` | shadcn/ui | MIT (connu) | composants UI | **ajoute une lib de composants** (décision lourde) | **deferred-to-refactor** | pertinent pour le design system Irminsul, mais introduit une dépendance → branche refonte uniquement |
| `improve-codebase-architecture`, `tdd` | mattpocock/skills | à vérifier | refactor/TDD | moyens (communauté) | **deferred-to-vet** | inspecter dépôt avant usage |
| `requesting/receiving-code-review`, `test-driven-development` | obra/superpowers | à vérifier | revue/TDD | moyens (communauté) | **deferred-to-vet** | possible chevauchement avec le rôle Codex/Claude existant |
| `sentry-cli` | sentry/dev | (Sentry) | error tracking | **service externe + secrets/compte** | **rejected** | introduit télémétrie externe + secrets ; contraire à « aucun secret inutile / pas d'exfiltration » |
| `high-end-visual-design`, `minimalist-ui`, `design-taste-frontend` | leonxlnx/taste-skill | non affichée | esthétique | **licence/source non vérifiables** | **rejected (pour l'instant)** | règle 6 (licence) non satisfaite ; auteur individuel non vérifié |

> Pas de candidat fiable trouvé pour : sécurité Tauri/IPC dédiée, threat modeling, secure-code-review
> spécialisé, performance Rust/Python, packaging Windows, accessibilité WCAG, visualisation de données.
> → privilégier un **skill local minimal** + les capacités natives de Claude Code (cf. décision globale).

## Décision globale (cette session)
**Installer 0 skill externe maintenant.** Raisons :
1. `find-skills` indisponible + skills.sh sans licence/source par skill → vérification incomplète (règles 1–10).
2. Phase PR #3 : ne pas ajouter de dépendance/contexte permanent avant la branche de refonte.
3. Les revues (sécurité, code, perf, a11y) sont déjà couvertes par **Claude (lead) + Codex (réviseur read-only)** ;
   un skill externe non vérifié n'apporterait pas de gain net sûr (règle 11).

## Plan d'adoption (branche `refactor/pro-ui-security`, après fusion PR #3)
1. Cloner/inspecter individuellement : `anthropics/skills`, `vercel-labs/agent-skills`, `shadcn/ui`
   (SKILL.md, scripts, deps, permissions, licence, maintenance, exfiltration). Consigner ici.
2. N'adopter que ceux qui passent les 12 règles ; sinon, écrire un **skill local minimal** ciblé
   (ex. `frontend-review`, `tauri-security-review`) chargé à la demande, sans dépendance externe.
3. Pour le design system : décider `shadcn` vs composants maison **dans la branche refonte** (impact dépendances).

## Statut
- Évalués : 7 familles de skills. **Installés : 0. Rejetés : 2. Différés (à vérifier) : 5.**
- Prochaine action skills : vetting repo-par-repo des candidats `deferred-to-vet` à l'ouverture de la branche refonte.
