# PERFORMANCE_AUDIT (2026-06-29) — lecture seule

> Beaucoup d'éléments sont **à mesurer** (pas encore instrumentés). On ne tire aucune conclusion non mesurée.

## Mesuré
- Bundle front : ≈ 158 kB JS (gzip ≈ 51 kB) — léger, pas de lib lourde.
- `vite build` ≈ 0.7–1.2 s ; `tauri build` ≈ 1 min 30 (Rust release + installeurs).
- Données mécaniques embarquées : `talent-multipliers.json` ≈ 1.5 Mo (le plus gros) ; sidecar onefile ≈ 9.6 Mo.

## Constats / risques (sévérité)
| # | Constat | Sév. | Impact | Correction | Statut |
|---|---------|------|--------|-----------|--------|
| P1 | **Sidecar onefile : extraction par appel** (1 process/requête) | moyen | latence par opération compte/calcul | mesurer ; si gênant, mode serveur long-vécu (déjà envisagé) ; sinon acceptable | to-measure |
| P2 | Listes (artéfacts/persos) **sans virtualisation** confirmée | moyen | jank sur gros inventaire | virtualiser (react-window/virtual) à la refonte, **après mesure** | to-measure |
| P3 | `talents_detail` ajouté au payload `character-stats` (≈10–20 attrs × 3 slots) | faible | payload + gros | OK actuel ; paginer/charger à la demande si besoin | to-measure |
| P4 | Pas de code-splitting / lazy-loading des vues | faible | TTI | `React.lazy` par route à la refonte | deferred |
| P5 | Memoization non mesurée | faible | sur/sous-optimisation | n'ajouter `useMemo`/`memo` **que mesuré** | deferred |

## À instrumenter (prochaine étape perf)
- Démarrage app (cold/warm), mémoire, latence sidecar par méthode (timing autour de `call_engine`).
- FPS/jank sur les listes du compte réel (gros roster).
- Taille/temps de parse des JSON mécaniques embarqués au démarrage du sidecar.

## Principe
Aucune optimisation sans **mesure avant/après**. Priorité : corriger d'abord ce qui est mesuré comme coûteux.
