# Roadmap vers 100 %

> Ordre critique pour faire monter MVP puis Vision (cf. `PROJECT_PROGRESS.json`).

## Pour atteindre ~75 % MVP
1. **packages/ui** : tokens OKLCH « Archive astrale » + composants de base (boutons, inputs, cartes, états).
2. **packages/engine-client** : interface typée vers le moteur (mock isolé d'abord).
3. **Vertical slice Laboratoire d'équipes** (`apps/web`) câblée à `TeamRepository` (Prisma) : sélection 4 persos, sauvegarde/chargement/suppression, états vide/loading/erreur, responsive + clavier.
4. **Tests** : E2E Playwright (sauver→recharger une équipe) + a11y axe.
5. **MCP next-devtools** : approbation interactive + appels réels (`get_routes`/`get_errors`).

## Pour atteindre ~90 %
6. Fusionner PR #3 (pont moteur) → brancher de **vraies** données moteur dans la slice (remplacer le mock).
7. Migrer les écrans desktop manquants (Tableau de bord, Équipes, gcsim, Assistant) vers le design system partagé.
8. Persistance étendue (builds, presets, snapshots) + repositories testés.

## Pour atteindre ~100 %
9. Couverture tests (unit + E2E + a11y) sur tous les flux critiques ; perf/bundle.
10. Packaging web (déploiement) + parité desktop ; assistant Claude (API) avec garde-fous.
11. Compléter les mécaniques moteur manquantes (réactions Lunaires, gcsim nouveaux persos).
12. (Optionnel, hors local-first) modules cloud Supabase si un besoin produit est validé.
