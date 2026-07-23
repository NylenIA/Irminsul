# Accessibilité Team Lab

> Test automatisé : `apps/web/tests/e2e/team-lab.spec.ts` (axe-core via `@axe-core/playwright`, tags `wcag2a`/`wcag2aa`), desktop + mobile. Critère : **0 violation critique/sérieuse**.

## Vérifié automatiquement (axe)
- Contraste (WCAG 1.4.3) : corrigé — `--irm-text-faint` relevé pour atteindre ≥ 4.5:1 (le libellé source échouait à 4.15).
- Labels/noms accessibles des champs (selects, inputs) ; ordre des titres (h1 → h2) ; rôles.

## Vérifié par construction
- **Clavier** : contrôles natifs (`select`, `input`, `button`) + dialog natif `<dialog>` (focus trap + Échap natifs).
- **Noms accessibles distincts** (finding Codex #3) : `aria-label="Renommer/Dupliquer/Supprimer <équipe>"`.
- **Confirmation de suppression** : `ConfirmDialog` (role `dialog`, nommé).
- **États** : `EmptyState`/`LoadingState` en `role="status"`, `ErrorState` en `role="alert"`.
- **Reduced motion** : `@media (prefers-reduced-motion: reduce)` neutralise animations/transitions.
- **Responsive** : grilles `auto-fit` + `clamp()` ; testé en viewport mobile (Pixel 5) et desktop.

## Restant (non bloquant)
- Annonce `aria-live` du succès d'une action (sauvegarde/suppression) — finding Codex #8 low, à ajouter.
- `<form onSubmit>` pour soumission clavier par Entrée — finding Codex #7 low.
