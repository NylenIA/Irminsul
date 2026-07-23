# Matrice d'audit statique des skills en quarantaine (15)

> Audité le 2026-07-04. **Aucun script exécuté.** Méthode : inventaire fichiers + lecture scripts
> + grep patterns dangereux + SHA-256. Détail machine : `SKILL_AUDIT_MATRIX.json`.

## Résultat global
- **Aucune opération destructrice** dans aucun skill (pas de `rmtree`/`os.remove`/`unlink`/`git push`/`git reset`/`git checkout`).
- **Egress réseau** : `design` (Google Gemini API + `GEMINI_API_KEY`), `senior-backend` (`api_load_tester.py` `urlopen`).
- **Subprocess** : `code-reviewer` (git read-only — l'auteur du détournement Codex de core-v1).
- **Tous untracked** → provenance/auteur/licence non prouvés → **aucun n'est `verified_allowed` pour Codex**.

## Verdicts
| Skill | Hash SKILL.md | Scripts | Réseau | Destructif | Codex | Verdict | Mission réelle |
|---|---|--:|:--:|:--:|:--:|---|---|
| design | 413f4ab9 | 8 | **oui** (Gemini) | non | ❌ | `verified_claude_only` | guidance couleurs/hiérarchie (scripts non exécutés) |
| senior-backend | 213d4445 | 4 | **oui** (load-test) | non | ❌ | `verified_claude_only` | principes contrats/erreurs du moteur |
| code-reviewer | 5cbee60a | 3 | non (git) | non | ❌ | `verified_claude_only` | revue **déléguée à Codex isolé**, pas à ce skill |
| senior-architect | 0e4ce066 | 3 | non | non | ❌ | `verified_read_only` | [ROTATION_ENGINE_ADR](../architecture/ROTATION_ENGINE_ADR.md) |
| senior-security | 8d550378 | 2 | non | non | ❌ | `verified_read_only` | audit sécurité sidecar rotation |
| senior-qa | 85d6970b | 3 | non | non | ❌ | `verified_read_only` | [ROTATION_ENGINE_TEST_MATRIX](../qa/ROTATION_ENGINE_TEST_MATRIX.md) |
| senior-frontend | 0f653401 | 4 | non | non | ❌ | `verified_read_only` | page `/rotations` |
| tdd-guide | faa63e59 | 8 | non | non | ❌ | `verified_read_only` | [ROTATION_TDD_TRACE](../qa/ROTATION_TDD_TRACE.md) |
| design-system | 655468bb | 7 | non | non | ❌ | `verified_read_only` | composants Timeline/StatBlock |
| ui-styling | f8b6c383 | 4 | non | non | ❌ | `verified_read_only` | polish responsive/focus/reduced-motion |
| ui-ux-pro-max | 603db520 | 4 | non | non | ❌ | `verified_read_only` | hiérarchie/densité /rotations |
| frontend-design-review | a595fe62 | 0 | non | non | ❌ | `verified_read_only` | grille de revue UI |
| brand | 6a450ee1 | 1 | non | non | ❌ | `verified_read_only` | cohérence Archive astrale |
| banner-design | 913d9c4b | 0 | non | non | ❌ | `verified_read_only` | SVG local (non prioritaire) |
| slides | 2b90bdaf | 0 | non | non | ❌ | `verified_read_only` | section rotations de la présentation |

## Règle appliquée
- `verified_read_only` / `verified_claude_only` : leur **guidance markdown** informe des livrables réels
  (documenté dans `SKILL_EFFECTIVENESS.md`). **Leurs scripts ne sont pas exécutés** (principe :
  ne jamais lancer un skill non vérifié/à egress pour « cocher une case »).
- **Codex** : `codex_scope=false` pour les 15. Les missions Codex tournent dans un worktree isolé
  qui n'hérite pas des untracked → protection structurelle (validée à la tranche précédente).
- Aucun skill `rejected` (pas d'op destructrice), aucun `missing`. Promotion en `verified_allowed`
  possible seulement après preuve de source + audit scripts + commit explicite.
