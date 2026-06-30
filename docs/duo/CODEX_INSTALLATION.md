# Installation Codex — état réel (2026-06-30)

| Élément | Résultat | Preuve |
|---|---|---|
| Package | `@openai/codex` (officiel, repo `github.com/openai/codex`) | `npm view` |
| Version | **0.142.4** (stable résolue) | `codex --version` → `codex-cli 0.142.4` |
| Installation | ✅ `npm install -g @openai/codex` (`added 2 packages`) | sortie npm |
| Chemin | `C:\Users\akuon\AppData\Roaming\npm\codex` | `which codex` |
| PATH | OK (dossier npm global déjà dans le PATH utilisateur) | aucune correction nécessaire |
| **Auth** | ❌ **non faite** — requiert `codex login` (navigateur, action utilisateur) | — |
| Test read-only | ⏳ après auth (`codex exec --sandbox read-only --ask-for-approval never`) | bloqué sur auth |

## Skills alirezarezvani (7) — cloné + audité, **installation bloquée**
- Source épinglée : `github.com/alirezarezvani/claude-skills` @ `4a3c05b69e64f4925f7fc65c88890f614f79caf0` (HEAD vérifié).
- Cloné dans le cache `~/.cache/irminsul-skills/...`. Variantes trouvées : `engineering-team/skills/<name>/` (Claude) et `.gemini/skills/<name>/`.
- **La copie dans `.claude/skills/` et `.agents/skills/` est refusée par le contrôle de sécurité « self-modification »** (l'agent n'installe pas des instructions issues d'un prompt téléchargé dans ses propres dossiers de comportement).
- **Déblocage = action utilisateur** : exécuter `scripts/bootstrap-codex-and-skills.ps1` (ou ajouter une règle de permission Bash pour cette copie). Le script est idempotent, audité, sources épinglées.

## Action utilisateur unique (regroupe les 2 étapes imposées par la sécurité)
```powershell
# 1) installe les 7 skills (copie dans .claude/.agents) + verifie codex
pwsh scripts/bootstrap-codex-and-skills.ps1
# 2) termine l'auth Codex (navigateur) puis reprend Duo
pwsh scripts/finish-codex-login.ps1
```
