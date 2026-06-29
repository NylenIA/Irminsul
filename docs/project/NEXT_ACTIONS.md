# NEXT_ACTIONS — prochaines actions exactes

> Ordre d'exécution pour la prochaine session. Mettre à jour après chaque lot validé.

## Décision en attente (propriétaire) — débloque un gros pan
1. **Besoin base de données ?** Énoncer la fonctionnalité utilisateur qui justifierait Supabase/Prisma
   (ex. sync multi-appareils, profils publics). Sinon → trancher « pas de cloud », web local-first.

## Prochaines actions techniques (sans nouveau « go »)
2. **`packages/ui`** : design system partagé (tokens OKLCH « Archive astrale » : quasi-noir `#0B0D11`,
   cyan désaturé, violet lunaire), consommé par `apps/web` ET (à terme) le desktop. Bâti UNE fois.
3. **`packages/engine-client`** : interface typée stable vers le moteur (abstrait `engine.ts`/sidecar),
   pour que l'UI web réutilise le moteur sans cloud.
4. **Vertical slice « Laboratoire d'équipes »** dans `apps/web` : navigation, design system, états
   loading/erreur/vide, données via engine-client OU **mock explicitement isolé** (tant que PR #3 non fusionnée).
   Test unitaire (Vitest) + E2E (Playwright) + contrôle a11y + responsive. Ne pas supprimer l'écran desktop.
5. **MCP next-devtools** : appliquer + tester en session interactive avec `npm run dev -w @irminsul/web`
   (cf. `docs/mcp/MCP_SETUP.md`). Puis `claude mcp list`.
6. **Continuité** : hook `SessionStart` idempotent (`.claude/hooks/`) lisant PROJECT_STATE + NEXT_ACTIONS ;
   skill `irminsul-project-orchestrator` (persistance). À faire après la slice.
7. **Recalcul d'avancement** : `FEATURE_MATRIX.md` + script reproductible `scripts/project_progress.py`
   (matrice pondérée → % vision + % MVP, intervalle, confiance, preuves). Remplace toute estimation à la main.

## Garde-fous permanents
- `export PATH="$HOME/.cargo/bin:$PATH"` avant `tauri:dev`.
- Aucune donnée de compte vers le cloud. Aucun secret dans Git. Pas de migration destructive.
- Commits atomiques. Pas de push/PR sans accord explicite.
