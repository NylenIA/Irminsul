# DESIGN_AUDIT (2026-06-29) — lecture seule

> Audit de surface (composants `App.tsx`, `views/Account.tsx`, `views/QuickCalc.tsx`). Plusieurs points UX
> sont **à vérifier** par un parcours réel ; aucune refonte appliquée ici.

## État actuel
- **Pas de design system central** : pas de tokens (couleurs/espacements/typo/rayons/ombres) formalisés ;
  styles via classes utilitaires maison (CSS global). Pas de lib de composants.
- **Duplication de patterns** : cartes/fiches répétées (Compte : personnages/armes/artéfacts) sans composant commun.
- **Vues** : Account (215 LOC), QuickCalc (413 LOC) — la calculatrice mêle formulaire, résultats, détail, panneaux.
- **Honnêteté UI** (point fort) : provenance/sources affichées, éléments « non pris en charge » signalés, pas de donnée factice.

## Constats (sévérité)
| # | Constat | Sév. | Impact | Correction (refonte) | Statut |
|---|---------|------|--------|----------------------|--------|
| D1 | Aucun design system / tokens | moyen | incohérence, dette | créer `app/src/design/` (tokens + primitives) | deferred-to-refactor |
| D2 | Composants dupliqués (cartes) | moyen | maintenance | bibliothèque de composants (Card, StatRow, ProvenanceBadge…) | deferred-to-refactor |
| D3 | **Accessibilité non vérifiée** (focus, clavier, ARIA, contraste, prefers-reduced-motion) | moyen | a11y/WCAG 2.2 AA | audit axe + tests clavier ; labels/roles | to-verify |
| D4 | Responsive / 1366×768 / zoom non vérifiés | moyen | utilisabilité | grilles fluides + tests responsive | to-verify |
| D5 | États vides/chargement/erreur/reconnexion incomplets | faible-moyen | UX | composants d'état standardisés | to-verify |
| D6 | Pas de thème clair/sombre formalisé (variables de thème) | faible | préférence/contraste | thèmes via tokens CSS | deferred |
| D7 | QuickCalc dense (beaucoup de champs) | faible | charge cognitive | progressive disclosure, regroupements | deferred |

## Direction recommandée (branche refonte)
- Identité sobre/premium, sombre par défaut + clair ; contraste élevé ; densité maîtrisée ; **pas de dépendance exclusive à la couleur** (icônes/texte d'état).
- Design system minimal **maison** d'abord (tokens + primitives), décision `shadcn` vs maison documentée (cf. SKILLS_AUDIT).
- Accessibilité testée (clavier, focus visible, reduced-motion, zoom, contraste).

## Prochaine étape design
1. Parcours réel + audit a11y (axe) → chiffrer D3/D4/D5.
2. Prototype isolé du design system (tokens + 5 primitives) **hors** branche PR #3.
