# Triage — audit de la tranche cœur V1 (données joueur + pages essentielles)

> Commits audités : `872bab6` (parseArtifactSets), `46b954b` (dashboard/characters/nav), `7abf665` (E2E).

## Incident Duo (transparent)
La mission Codex read-only (`gpt-5.4-mini`, `-o codex-audit-core-v1.md`) a d'abord **auto-chargé un
skill `code-reviewer` non suivi** (`.agents/skills/`) et suivi *ses* règles (lecture de
`universal.md`/`typescript.md`) — le reçu est resté vide un long moment. Il **est finalement arrivé**
(Codex était simplement lent) avec 1 finding Low exploitable. Leçon conservée : un skill non vérifié
peut dégrader/ralentir une mission → **ne jamais faire confiance à / commiter un skill non vérifié**.

## Triage des findings
| # | Sévérité | Finding | Décision | Correction / Test |
|---|---|---|---|---|
| 1 | **Low** | `parseArtifactSet`/`parseWeaponRef` acceptaient un suffixe `[0-9a-f]+` de longueur quelconque, alors que `_short_hash` (src/irminsul/account.py) émet **exactement 8 hex** → un ref tronqué/trop long pouvait être compté comme un vrai set badge | **accepted + fixed** | regex verrouillée `[0-9a-f]{8}` + `\d{3,}` sur les deux parseurs ; **4 cas négatifs ajoutés** (hash 7/9/non-hex, slot inconnu) — vitest 45/45 |

## Vérifications positives (confirmées par Codex ET la relecture Fable)
| Point | Verdict | Preuve |
|---|---|---|
| Fuite `source_path` / payload brut | **OK** | type de `profile` restreint à `{snapshot_date, source, format}` → chemin local `E:\…` structurellement inaccessible ; seul le DTO normalisé rendu |
| Frontière serveur/client | **OK** | `account.ts` (`node:fs`) importé seulement par Server Components (`force-dynamic`) → jamais en bundle client ; build PASS |
| Aucune stat inventée | **OK** | `/characters` affiche « stats finales non affichées, jamais estimées » ; valeurs scannées uniquement |
| Accessibilité nav | **OK** | `<nav aria-label>` + `:focus-visible` ; axe **0 critique/sérieux** sur `/`, `/characters`, `/team-lab` |

**Verdict Codex : « Globalement bon, corriger le parseur d'artéfacts avant merge » → fait.**

## Gates (post-correctif)
vitest engine-client **45/45** · build + TypeScript **PASS** · E2E Playwright **16/16** (desktop+mobile) · axe **vert** 3 pages.
