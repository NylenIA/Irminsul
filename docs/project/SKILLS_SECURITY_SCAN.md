# SKILLS_SECURITY_SCAN — résultats SkillSpector (2026-06-29)

> Scanner : **NVIDIA SkillSpector v2.3.7** (commit `78be329`), installé en venv isolé via `uv` (Python 3.13),
> **mode statique `--no-llm`, sans aucune clé API**. Score : **plus haut = plus risqué** (0 = sûr, 100 = critique).
> Aucun skill flaggé HIGH/CRITICAL n'est installé (porte de sécurité respectée).

## Méthode
1. **Vérification d'existence/légitimité** de chaque source (API GitHub / registre npm) avant toute exécution.
2. **Clonage en quarantaine** (`.irminsul/skilltools/quarantine/`, gitignoré) — aucun code exécuté à ce stade.
3. **Scan SkillSpector statique** de chaque skill candidat.
4. Installation **uniquement des LOW** dans l'espace **isolé** du fork Duo (`../duo-agents-fork/.claude/skills/`),
   **hors** du dépôt Irminsul / contexte PR #3.

## Résultats du scan (9 candidats à SKILL.md)
| Skill | Source @commit | Score | Sévérité | Constats | Décision |
|---|---|---|---|---|---|
| frontend-design | anthropics/claude-code @01f1617 | 13 | LOW | 1 | **installé** |
| frontend-design-review | microsoft/skills @fddb721 (MIT) | 0 | LOW | 0 | **installé** |
| senior-architect | alirezarezvani/claude-skills @4a3c05b (MIT) | 12 | LOW | 2 | **installé** |
| senior-qa | alirezarezvani @4a3c05b (MIT) | 17 | LOW | 21 | **installé** |
| senior-frontend | alirezarezvani @4a3c05b (MIT) | 47 | **MEDIUM** | 4 | **différé** |
| tdd-guide | alirezarezvani @4a3c05b (MIT) | 21 | **MEDIUM** | 3 | **différé** |
| senior-backend | alirezarezvani @4a3c05b (MIT) | 52 | **HIGH** | 18 | **différé** |
| senior-security | alirezarezvani @4a3c05b (MIT) | 57 | **HIGH** | 13 | **différé** |
| code-reviewer | alirezarezvani @4a3c05b (MIT) | 100 | **CRITICAL** | 13 | **rejeté (as-is)** |

## Pourquoi les différés/rejetés
- **code-reviewer (CRITICAL)** : embarque des **scripts Python exécutables** (`scripts/pr_analyzer.py`,
  `scripts/review_report_generator.py`) appelant `subprocess`, **sans permissions déclarées** (LP3 :
  « no declared permissions but code capabilities: file_read, file_write, shell »). Risque shell non gouverné
  (écho de l'incident `engine.ts`).
- **senior-backend / senior-security (HIGH)** + **senior-frontend / tdd-guide (MEDIUM)** : scores élevés
  (scripts embarqués / capacités shell-fichier non déclarées / instructions d'action autonome `EA2`).
- → Non installés **as-is**. Option proposée (à valider) : version **assainie** (SKILL.md + références **sans**
  le dossier `scripts/` exécutable) → réduit le risque tout en gardant la guidance. Sinon : utiliser **Codex +
  Claude** (déjà en place) pour revue/backend/sécurité.

## ui-ux-pro-max (npm `ui-ux-pro-max-cli` 2.9.0, mrgoonie) — **différé**
- Paquet **sans script postinstall** (install sûr), deps standards. MAIS le CLI `dist/index.js` utilise
  `child_process`/`spawn` + `fetch` + **API GitHub + « github.com/settings/tokens »** → comportement réseau /
  token non vérifiable sans **exécuter** le CLI. Le skill `ui-ux-pro-max` est **généré au runtime** par `uipro init`
  (donc non scannable statiquement). → **non exécuté** dans l'environnement principal ; à évaluer en sandbox dédiée.

## Skills installés — vérifications §7 (toutes ✅)
SKILL.md présent · frontmatter `name:` valide · noms uniques · **0 lien cassé** · **0 vrai secret** (les matches
dans `senior-qa/references/test_automation_patterns.md` sont des **exemples de tests** `password:string`, pas des
secrets) · scripts **sans** `subprocess`/réseau · taille raisonnable.

## Emplacement (isolé)
`C:/Users/akuon/IA Genshin/duo-agents-fork/.claude/skills/` — **séparé** du dépôt Irminsul (PR #3 non polluée).
Quarantaine + venv outil : `.irminsul/skilltools/` (gitignoré).
