# AGENT_BOARD — répartition Claude Code / Codex (via Duo)

> Claude Code = **lead developer + orchestrateur** (décide, implémente, teste, trie, commit, PR).
> Codex (via `duo run`) = **réviseur indépendant** / worker isolé borné. Codex ne push jamais sur
> `main`, ne fusionne jamais, ne modifie jamais les mêmes fichiers que Claude en parallèle.

## Règles de coordination
- Un seul agent écrit dans un fichier donné à la fois (pas d'édition parallèle).
- Toute mission Codex est **bornée** : objectif, fichiers autorisés/interdits, critères, tests, format de rapport.
- Claude **reproduit** chaque constat Codex avant de l'accepter (`accepted` / `rejected-with-evidence` / `deferred-with-reason`).
- Revue indépendante obligatoire avant fusion pour tout changement mathématique/sécurité/import/sidecar/CI.

## Outils
- `duo doctor` ✅ (Claude Code 2.1.195, Codex CLI 0.142.3). Config : `duo.config.json` (sandbox Codex `workspace-write`).
- Missions : `docs/project/duo/current-task.md` · Rapports : `docs/reviews/`.

## Tableau

| ID | Tâche | Responsable | Réviseur | Branche/worktree | État |
|----|-------|-------------|----------|------------------|------|
| T1 | Stats de base **perso** (basestats) | Claude | Codex | feat/combat-engine-phase3 | ✅ implémenté (5167954) + correctifs revue (C1–C6) |
| P1 | Confidentialité mémoire d'agent (§5.1) | Claude | — | feat/combat-engine-phase3 | ✅ untrack+gitignore (39cf48f) ; purge reflog local = **attente autorisation** |
| R1 | Revue indépendante diff PR #3 (base stats) | Codex | Claude | lecture seule | ✅ **changes-required** → 6 constats, tous corrigés (`docs/reviews/CODEX_PR3_BASESTATS_REVIEW.md`) |
| R2 | Contre-revue Codex des correctifs | Codex | Claude | lecture seule | ✅ **changes-required** → résidus C3/C5 corrigés (commit `cfa13a6`), 181 tests |
| T2 | Stats de base **armes** (weaponstats) | Claude | Codex | feat/combat-engine-phase3 | ✅ implémenté (236 armes) ; registre `probable` |
| T3 | Stats finales auto complètes (ATQ arme) | Claude | Codex | feat/combat-engine-phase3 | ✅ ATQ finale `complete=true` ; champ ATQ UI masqué auto ; durci (R3 #4) |
| R3 | Revue Codex stats d'armes (golden indép.) | Codex | Claude | lecture seule | ✅ **changes-required** : 10 armes croisées wiki OK ; #4/#5 corrigés (`docs/reviews/CODEX_PR3_WEAPONSTATS_REVIEW.md`), 202 tests |
| T4 | Multiplicateurs de talents (module + câblage) | Claude | Codex | feat/combat-engine-phase3 | ✅ module (`67a3b80`) + **câblage charstats/UI** (`048eca2`) : sélecteur de talent remplace la saisie `scaling` ; 225 tests |
| T5 | Durcissement extraction armes + `verified` | Claude | Codex | feat/combat-engine-phase3 | ✅ hash+dirty-check ; **weapon_base_stats = `verified`** (`e83faf5`) sur base R3 indép. |
| R4 | Revue Codex talents (golden indép.) | Codex | Claude | lecture seule | ⛔ **bloquée : quota Codex** (réessayer ~03:58) → gate de fusion talents |
| P2 | Purge UID (reflog + message commit publié) | Claude | — | feat (réécriture) | ✅ **RÉSOLU** : option A — réécriture messages `feat` (`filter-branch`+`--force-with-lease`, arbre identique), UID purgé local+distant ; `main`/tags intacts |
| INC | Incident suppression `engine.ts` | Claude | — | feat | ✅ restauré (`dd71f19`) ; isolation Codex read-only + test intégrité (`a314356`) ; scheduler désactivé |

## Correctifs §5 (triage)
- **5.1 Confidentialité mémoire → traité** (P1) ; purge historique local (commits pendants) en attente d'accord.
- **5.5 Validation math → traité** (C3 : NaN/inf rejetés ; property tests) via revue R1.
- **5.6 Golden indépendants → vérifié** : goldens basestats ancrés sur valeurs **en jeu** (Ayaka 12858, Hu Tao 15552/106), pas sur la formule du code.
- 5.2 Intégrité import GOOD · 5.3 agent `irminsul-developer` · 5.4 sécurité sidecar · 5.7 CI repro · 5.8 docs →
  **à auditer/prioriser** (prochaine revue Codex quand le quota est rétabli) puis traiter par gravité.
