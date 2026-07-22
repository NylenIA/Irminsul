# Handoff de session — reprise Irminsul (full auto)

> À lire en premier par une nouvelle session Claude Code. État figé au commit
> `7031946` (branche `feat/irminsul-complete-redesign`, synchro avec origin, tracked clean).
> **MVP utilisable : 89 %** (`scripts/project_progress.py`, `docs/project/PROJECT_PROGRESS.md`).

## Mode de travail (imposé par Nylen)
- Tu es **lead dev autonome, full auto**. N'utilise plus Duo. Délègue à **Codex seulement si gain réel**
  (sinon fais-le toi-même). Utilise **les skills** (`.claude/skills/`) **systématiquement** selon la tâche
  (senior-security/frontend/qa, tdd-guide, code-reviewer, design, brand, genshin-dps, genshin-source-verifier…).
- **Ne demande pas quoi faire ensuite** si tu peux le déterminer. N'interromps que pour : décision
  fonctionnelle majeure, risque de perte de données, action irréversible, auth/permission.
- Français. **Zéro donnée inventée** ; sépare OFFICIEL/LIVE/THÉORYCRAFT/SIMULATION/LEAK ; toute formule sourcée (KQM).

## Boucle par cycle (à répéter)
1. Choisir le plus petit incrément livrable (le plus rentable au MVP).
2. Implémenter (TDD quand pertinent) ; fichiers nécessaires seulement.
3. **Gates** : `npm run verify` (typecheck + ruff `lint:py` + eslint `lint:web` + vitest×3 + pytest `test:py`
   + build + `check:proxy`) **et** `npm run test:e2e -w @irminsul/web` (Playwright, axe inclus).
4. Corriger à la RACINE (jamais contourner), relancer, **committer atomique**, **pousser** (`git push`),
   puis mettre à jour `PROJECT_PROGRESS.json` + régénérer via `python scripts/project_progress.py`.
   Fin de commit : `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## Commandes / faits techniques (Windows, Git Bash)
- Ne pas travailler sur `main`, `feat/combat-engine-phase3`, `duo-agents-fork`. Branche = `feat/irminsul-complete-redesign`.
- Python : `.venv/Scripts/python.exe` ; **chemins exe en backslash** dans package.json (cmd rejette `/`).
- Rust/Tauri : `export PATH="$HOME/.cargo/bin:$PATH"` avant `tauri`. Desktop : `npm run desktop:build`.
- Après TOUTE modif du moteur Python : `npm run desktop:sidecar` (rebuild binaire gelé, sinon les gardes
  de parité `test_sidecar_binary.py` cassent).
- Réactions : source de vérité `src/irminsul/reaction.py`, miroir TS `packages/engine-client/src/reactions.ts`,
  parité par **goldens croisés** (`scripts/gen-reaction-goldens.py` → régénérer ; gardes py+ts).
- E2E : DB SQLite isolée `.e2e/` ; `global-setup.ts` durci contre EPERM Windows (retry). Nettoyer
  `apps/web/.e2e/*.db*` avant un run si besoin. Chromium Playwright déjà installé.
- Avertissements `LF will be replaced by CRLF` = bénins. Le scan GOOD réel existe (`data/account/current/`)
  → assertions E2E **indépendantes du scan** (invariants), pas de valeurs figées.
- **Ne PAS** committer : `data/account/`, `.irminsul/` (gitignorés). `data/mechanics/*.json` = données de
  jeu sourcées versionnées (gros mais normal — c'est ~84k lignes du diff de branche).

## Directives Nylen — état
1. ✅ Logo + design + animations légères (logo SVG `IrminsulLogo.tsx`, favicon `/icon.svg`, icône desktop,
   `docs/design/BRAND_GUIDE.md`, primitives Select/Toast/CharacterPicker).
2. ✅ **Formules vérifiées** → `docs/engine/FORMULA_SOURCES.md`. **Bug DPS corrigé** : coefficients
   transformatifs pré-5.2 → post-5.2 (EC 2.0, Overload 2.75, Superconduct 1.5, Shatter 3.0 — 3 sources).
3. ✅ **Veille** → `docs/engine/PATCH_WATCH.md` (process + checklist par patch + `irminsul update`/`status`).
4. ✅ Certificat de signature **abandonné** (distribution privée entre amis) → plus un blocage.

## Décisions verrouillées / gotchas
- **Lunar-Bloom EXCLU** : multiplicateur non confirmé KQM → rejet explicite. Pipeline prêt (2 constantes + goldens dès source rang A).
- **Codex CLI cassé** ici : sandbox `0xC0000142`. Voir `docs/reviews/CODEX_DUO_ACCESS_REPORT.md`. Chemin
  fiable = app Codex desktop (Nylen la lance) OU faire soi-même. Ne pas promettre du Codex CLI autonome.
- gcsim `add stats` = contribution ARTEFACTS (pas totaux) sinon double-comptage. Gate strict 5★ niv20 (`artifact-stats.ts`).
- **local-first** : aucune donnée privée vers le cloud.

## Hook SessionStart (continuité — item ouvert)
Script `.claude/hooks/irminsul-session-start.ps1` existe (idempotent, lecture seule). À enregistrer dans
`.claude/settings.json` :
```json
{ "hooks": { "SessionStart": [ { "matcher": "startup|resume|clear|compact",
  "hooks": [ { "type": "command", "command": "pwsh -NoProfile -File .claude/hooks/irminsul-session-start.ps1" } ] } ] } }
```

## Scores par domaine (89 % global)
Team builder 95 · Intégration moteur 91 · Moteur 90 · App web 89 · Design 86 · Packaging 85 ·
App desktop 84 · Tests 84 · Persistance 82 · Documentation 82.

## Backlog priorisé (prochains cycles)
1. **Persistance 82** — couverture `TeamRepository` (data-access vitest) : import transactionnel avec
   rollback, ou chemin DB desktop `%APPDATA%`.
2. **Tests 84** — tests unitaires jsdom des composants UI (aujourd'hui couverts seulement en E2E).
3. **App desktop 84** — finitions (MSI par conception ; chemins données).
4. **Documentation 82** — enregistrer le hook SessionStart ci-dessus.
5. Externe : **Lunar-Bloom** dès source KQM ; revalider les constantes à chaque patch (PATCH_WATCH).

## Où NE PAS retourner
Mission « desktop V2 » finie ; routeur Duo abandonné. Ne relance pas de gros cycles si les preuves
existent déjà (`.irminsul/logs/gate-*.log`, `.irminsul/proof/`).
