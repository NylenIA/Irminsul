# Brand guide — Irminsul

> L'**intention** de marque derrière le [design system](DESIGN_SYSTEM.md) (l'implémentation).
> Direction : « Archive astrale » — un observatoire tactique, sombre, froid, premium et vivant.

## 1. Nom & sens
**Irminsul** — dans le lore de Genshin, l'arbre-mémoire qui archive tout le savoir de Teyvat.
Le produit porte ce nom parce qu'il est un **outil de connaissance et de calcul rigoureux** :
il archive, vérifie et calcule — jamais il n'invente. Le nom engage à l'exactitude.

**Promesse** : des chiffres et des recommandations **transparents, sourcés et honnêtes** pour
un vrai joueur — jamais de faux DPS, jamais de leak présenté comme confirmé.

## 2. Voix & ton
- **Précis et sobre.** On donne un chiffre avec ses hypothèses, jamais un chiffre nu.
- **Honnête sur l'incertitude.** « SIMULATION », « squelette — à affiner », « TODO » : on nomme
  ce qui n'est pas prouvé plutôt que de le maquiller. Séparer OFFICIEL / LIVE / THÉORYCRAFT /
  SIMULATION / LEAK / SPÉCULATION.
- **Au service du joueur réel.** On adapte au compte (armes, constellations, artéfacts, confort).
  Jamais « plafond théorique » présenté comme « performance pratique ».
- **Français par défaut**, vocabulaire Genshin exact. Ni hype, ni jargon IA générique.

**À éviter** : superlatifs vides (« le meilleur build ultime »), certitudes non sourcées,
ton condescendant, anglicismes inutiles.

## 3. Couleurs (psychologie, tokens réels)
Palette OKLCH, fond quasi-noir bleuté — un ciel d'observatoire, pas une UI SaaS blanche.
| Couleur | Token | Sens | Usage |
|---|---|---|---|
| Turquoise spectral | `--irm-cyan` | donnée vérifiée, action, focus mental | accent principal, titres, primary |
| Violet lunaire | `--irm-violet` | le rare, le nocturne (réactions lunaires) | **parcimonieux** |
| Or | `--irm-gold` | valeur, mise en avant chiffrée clé | **très contrôlé** |
| Rouge tension | `--irm-danger` | risque, destruction, erreur | rare, jamais décoratif |
| Ivoire froid | `--irm-text` | lisibilité | jamais blanc pur |

Règle d'or : **la profondeur vient de la matière** (couches de surfaces, ombres légères),
pas des effets. Pas de néons, pas de glassmorphism généralisé, pas de copie de l'UI Genshin.

## 4. Typographie
- Interface : `--irm-font` (Segoe UI / system-ui) — neutre, dense, lisible sur écrans chargés.
- Données/config : `--irm-mono` (Cascadia Code) — chiffres et scripts gcsim alignés.
- La typo décorative reste **rare** : les écrans denses priment.

## 5. Logo (direction, non produit ici)
Pas encore d'asset final. Direction recommandée pour une itération future (skill `brand`/`design`) :
- Motif : un **arbre/constellation stylisé** — branches = lignes de données, nœuds = étoiles.
- Monochrome turquoise sur fond `--irm-bg` ; version 1 couleur pour favicon/menu Démarrer.
- Géométrique, fin, lisible à 16px (icône desktop). Éviter le détail organique réaliste.
- Décision ouverte à Nylen ; à générer avec la skill `design` quand souhaité.

## 6. Accessibilité = partie de la marque
Focus visible, navigation clavier, contraste (`prefers-contrast: more`), `prefers-reduced-motion`,
`aria-live` pour le feedback. Une marque « rigoureuse » qui exclut des utilisateurs se contredit.

## 7. Application (checklist rapide)
- [ ] Un chiffre affiché a ses hypothèses/provenance à portée de clic.
- [ ] Accent cyan par défaut ; violet/or/rouge seulement si le sens l'exige.
- [ ] Aucun état sans feedback (succès → toast ; erreur → message explicite).
- [ ] Aucune donnée inventée ; l'incertitude est nommée.
- [ ] Contraste, focus, reduced-motion vérifiés (axe 0 critique en E2E).
