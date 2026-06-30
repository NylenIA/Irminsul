# Session handoff — comment reprendre

## À lire en premier (ordre)
1. `docs/project/PROJECT_STATE.md` (état) · 2. `docs/project/NEXT_ACTIONS.md` (prochaines actions) ·
3. `docs/project/DECISIONS.md` (décisions verrouillées) · 4. `docs/project/ARCHITECTURE.md`.

## Branche & garde-fous
- Travailler sur **`feat/irminsul-complete-redesign`** uniquement. Ne pas toucher `main`, `feat/combat-engine-phase3`, `duo-agents-fork`.
- `export PATH="$HOME/.cargo/bin:$PATH"` avant tout `tauri:dev`/`tauri:build`.
- Décision verrouillée : **local-first** ; pas de donnée privée vers le cloud.

## Hook SessionStart (continuité automatique)
Script : `.claude/hooks/irminsul-session-start.ps1` (idempotent, lecture seule).
Enregistrement à ajouter dans `.claude/settings.json` (événements startup/resume/clear/compact) :
```json
{ "hooks": { "SessionStart": [ { "matcher": "startup|resume|clear|compact",
  "hooks": [ { "type": "command", "command": "pwsh -NoProfile -File .claude/hooks/irminsul-session-start.ps1" } ] } ] } }
```
Vérif idempotence : `pwsh scripts/verify-session-context.ps1` (20 appels, aucun changement d'état).

## Action utilisateur unique (n'empêche rien)
- Approuver le MCP `next-devtools` : `/mcp` dans un terminal Claude Code (cf. `scripts/approve-project-mcps.ps1`).
- Supabase (optionnel, plus tard) : `scripts/configure-supabase-mcp.ps1 -ProjectRef <dev>` + `claude mcp login supabase`.
