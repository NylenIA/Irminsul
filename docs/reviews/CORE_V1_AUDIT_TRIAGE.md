# Triage — audit de la tranche cœur V1 (données joueur + pages essentielles)

> Commits audités : `872bab6` (parseArtifactSets), `46b954b` (dashboard/characters/nav), `7abf665` (E2E).

## Incident Duo (transparent)
La mission Codex read-only (`gpt-5.4-mini`, `-o codex-audit-core-v1.md`) **n'a produit aucun
reçu de findings** : Codex a auto-chargé un **skill `code-reviewer` non suivi** présent dans
`.agents/skills/` et a suivi *ses* règles (lecture de `universal.md`/`typescript.md`, génération
d'un rapport générique) au lieu de mon prompt ciblé. Le log (1887 lignes) montre la lecture des
règles + des diffs, mais jamais le message final attendu. **Cas B→C** de l'arbre de décision.

**Décision** : ne PAS relancer Codex (le même skill non suivi le re-détournerait), mais réaliser
la contre-revue comme **relecteur Fable** de la boucle Duo, chaque point vérifié contre le code
réel + preuves de tests. Ceci renforce la règle permanente : **ne jamais faire confiance à / commiter
un skill non vérifié** — ici il a activement dégradé une mission.

## Contre-revue Fable (vérifiée contre le code)
| # | Point audité | Verdict | Preuve |
|---|---|---|---|
| 1 | Fuite de données perso | **OK** | `account.ts` type `profile` à `{snapshot_date, source, format}` uniquement → `source_path` (chemin local `E:\…`) **structurellement inaccessible** ; seul le DTO `PlayerCharacterBuild[]` normalisé est rendu, jamais le payload brut |
| 2 | Robustesse `parseArtifactSet` | **OK** | regex ancrée + slot whitelisté ; réf malformée → `null` filtré. Testé (`ref-invalide` → `[]`) |
| 3 | Frontière serveur/client | **OK** | `account.ts` (`node:fs`) importé seulement par Server Components (`page.tsx`/`characters/page.tsx`, pas de `"use client"`, `force-dynamic`) → jamais en bundle client. Build PASS |
| 4 | Aucune stat inventée | **OK** | `/characters` affiche explicitement « stats finales non affichées, jamais estimées » ; niveaux/talents/sets = valeurs scannées uniquement |
| 5 | Accessibilité nav | **OK** | `<nav aria-label>`, liens `irm-btn--ghost` avec `:focus-visible` ; **axe 0 critique/sérieux sur `/`, `/characters`, `/team-lab`** |

**Verdict global : Approve.** Aucun finding High/Medium. 0 correctif requis sur le code de la tranche.

## Gates (post-triage, inchangés)
vitest engine-client **44/44** · build + TypeScript **PASS** · E2E Playwright **16/16** (desktop+mobile) · axe **vert** 3 pages.
