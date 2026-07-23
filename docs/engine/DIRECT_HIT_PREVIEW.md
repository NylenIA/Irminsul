# Aperçu de coup direct — périmètre, provenance, limites

> Première intégration moteur→UI (ADR : `docs/architecture/TEAM_LAB_COMBAT_ENGINE_ADR.md`).
> Contrat : `direct-hit/1.0` (`packages/engine-client`).

## Ce qui est calculé
Un **coup isolé** déterministe : dégâts sans critique / critique / **attendu** (moyenne pondérée
par le taux crit), multiplicateurs DEF et RES. Formule `calculate_direct_hit` du moteur Python
(statut registre **verified**, goldens croisés en jeu), portée en TS avec **parité prouvée**
(9 goldens générés du moteur réel, tolérance 1e-9 + garde pytest inverse).

## Ce qui N'est PAS calculé (affiché à l'utilisateur)
- Pas un **DPS de rotation** ni un dégât d'équipe (gcsim pour cela).
- Pas de buffs/débuffs déduits automatiquement (à saisir en entrée).
- Pas de réactions amplifiantes implicites (v1 : multiplicateur non exposé dans l'UI).
- Pas de stats de personnage réelles : l'utilisateur saisit multiplicateur + stat porteuse
  (**saisie contrôlée** ; le roster ne fournit que l'identité). Le câblage aux builds importés
  viendra du scan de compte (desktop/sidecar) — rien n'est inventé d'ici là.

## Flux
`DirectHitPreview (client)` → `previewDirectHitAction` (Server Action mince) →
`buildDirectHitPreview` (pur, testé : validation, défauts listés, %→décimal) →
`LocalEngineClient.calculateDirectHit` → résultat + provenance + hypothèses + version contrat.

## États UI
`idle · loading (skeleton) · success · insufficient_data (champs requis listés, rien d'inventé)
· validation_error · engine_error · stale_contract (version client ≠ serveur)`.
Accessibilité : labels explicites, `role=status/alert`, reduced-motion (ligne d'énergie s'arrête
après 2 passages, shimmer désactivé), contraste AA (axe vert), clavier natif.

## Confiance
`haute` — formule au statut « verified » du registre des mécaniques. Les valeurs par défaut
utilisées (crit 5/50, RES 10 %, niveaux 90/100) sont **listées avec le résultat** (badge
« défauts utilisés ») : l'aperçu est fidèle au build seulement si l'utilisateur saisit ses stats.

## Prochaines formules (goldens-first, ADR §Périmètre)
Réactions amplifiantes exposées dans l'UI → additives (Aggravate/Spread) → transformatives →
lien avec les builds réels importés.
