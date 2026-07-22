# Design system Irminsul — « Archive astrale »

> Source : `packages/ui`. Direction : observatoire tactique sombre et vivant ; profondeur par la
> matière, pas par les effets ; froid, premium, sobre. Pas de glassmorphism généralisé, pas de
> néons, pas d'interface IA générique, pas de copie de l'UI Genshin.

## Tokens (`packages/ui/src/styles/tokens.css`, OKLCH)
| Rôle | Token | Note |
|---|---|---|
| Fond | `--irm-bg` | quasi-noir bleuté |
| Surfaces | `--irm-surface-1/2`, `--irm-border(-strong)` | graphite, profondeur par couches |
| Texte | `--irm-text` (ivoire froid), `--irm-text-dim/faint` | jamais blanc pur |
| Accents | `--irm-cyan(-dim)` (turquoise spectral), `--irm-violet` (lunaire, **rare**), `--irm-gold` (**très contrôlé**), `--irm-danger` (tension chaude, rare) |
| Focus | `--irm-focus` | contour visible 2px |
| Motion | `--irm-dur-fast/-/-slow`, `--irm-ease` | transitions calmes ; `prefers-reduced-motion` respecté |
| Forme | `--irm-r-sm/-/-lg`, `--irm-space`, `--irm-shadow` | rayons mesurés, ombres légères |

## Composants (`packages/ui/src/components`)
- **Button** : `default | primary | ghost | danger` ; états hover/active/focus-visible/disabled.
- **Card** : surface 1, titre cyan optionnel.
- **Input / Select** : surface `.irm-input` commune ; Select masque l'apparence native, chevron aux tokens, `option/optgroup` stylés ; a11y par `aria-label`.
- **EmptyState / LoadingState / ErrorState** : `role=status|alert`, invite à agir / annonce l'attente / explique l'erreur.
- **ConfirmDialog** : `<dialog>` natif, backdrop assombri, actions confirmer/annuler.
- **Toast / Toaster** : feedback non bloquant, `role=status aria-live=polite`, variantes succès/erreur/info, auto-dismiss, reduced-motion safe. Store module-level (`toast()` partout, `<Toaster/>` une fois dans le layout).
- **CharacterPicker** (app, domaine Genshin) : sélecteur de roster « Nom · Élément », exclusion d'équipe encapsulée.

## Règles d'usage
- Importer `@irminsul/ui/tokens.css` une fois (layout) ; appliquer `.irm-root` sur `<body>`.
- Densité maîtrisée, hiérarchie immédiate ; la typo décorative reste rare (écrans denses d'abord).
- Accessibilité : focus visible, navigation clavier (contrôles natifs), contraste (mode `prefers-contrast: more`), reduced-motion.
- Accents `violet`/`gold` : usage parcimonieux ; couleurs élémentaires seulement quand la donnée l'exige.

## À compléter (prochaines primitives)
Tooltip, Panel, TeamSlot. **Tabs différé (YAGNI)** : aucune surface n'en a besoin aujourd'hui ;
à créer quand un écran le justifie. Badge existe en classe utilitaire (`.irm-badge`) ; le promouvoir
en composant si l'usage se diversifie.

## Identité de marque
Voir [BRAND_GUIDE.md](BRAND_GUIDE.md) — nom, voix, logo, psychologie des couleurs, do/don't.
Le design system (tokens/composants) est l'**implémentation** ; le brand guide en est l'**intention**.
