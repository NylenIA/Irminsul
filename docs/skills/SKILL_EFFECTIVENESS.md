# Registre de confiance des skills (véridique, preuve disque 2026-06-30)

> Source de vérité : `SKILL_EFFECTIVENESS.json` (vérifiable par `scripts/verify-skill-registry.ps1`).
> **Correction du prompt §12.1** : sa table suppose 16 skills installés ; le disque en montre **3**.
> Détection Codex = **n/a** partout (Codex CLI absent).

| Skill | Version/commit | Install. complète | Détecté Claude | Détecté Codex | Missions réelles | Tests | Confiance |
|---|---|:--:|:--:|:--:|--:|--:|---|
| frontend-design | anthropics (fichier) | ✅ | ✅ | n/a | 0 | 0 | candidate |
| skill-creator | anthropics/skills | ✅ | ✅ | n/a | 0 | 0 | candidate |
| webapp-testing | anthropics/skills | ✅ | ✅ | n/a | 0 | 0 | candidate |
| senior-architect | alirezarezvani (revendiqué @4a3c05b) | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| senior-backend | alirezarezvani | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| senior-security | alirezarezvani | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| senior-frontend | alirezarezvani | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| senior-qa | alirezarezvani | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| code-reviewer | alirezarezvani | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| tdd-guide | alirezarezvani | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| ui-ux-pro-max | npm CLI 2.9.0 (skill non installé) | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| frontend-design-review | microsoft (revendiqué) | ❌ | ❌ | n/a | 0 | 0 | **absent** |
| design / design-system / ui-styling / brand / banner-design / slides | npm 2.9.0 (revendiqué) | ❌ | ❌ | n/a | 0 | 0 | **absent** |

## Promotion (rappel)
`absent → untrusted` (installé+détecté) → `candidate` → `qualifying` (1 mission réelle + sortie + tests) → `qualified` (≥2 missions + revue croisée + gates vertes). Aucune promotion sans preuve.

## Déblocage
- Installer les 15 skills absents depuis **sources réelles vérifiées** (ne pas inventer ; plusieurs noms/commits du prompt sont à confirmer — cf. leçon `figma-implement-design` inexistant).
- Détection Codex impossible tant que Codex CLI n'est pas installé+authentifié.
