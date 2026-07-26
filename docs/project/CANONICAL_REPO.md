# Dépôt canonique Irminsul — identification (préflight redesign)

> Établi le 2026-06-30 au lancement de la mission « refonte complète ».
> Toutes les valeurs ci-dessous proviennent de commandes git exécutées, pas d'hypothèses.

## Dépôt canonique retenu

| Élément | Valeur (vérifiée) |
|---|---|
| Chemin racine (`git rev-parse --show-toplevel`) | `<racine locale>/Irminsul-AI-Claude-Code` |
| Remote `origin` | `https://github.com/NylenIA/Irminsul.git` ✓ (= `NylenIA/Irminsul` attendu) |
| `main` local | `bfb6a04` = `origin/main` (Phase 0-3 #2) |
| Branche de travail créée | `feat/irminsul-complete-redesign` (basée sur `main`) |

C'est le **seul** dépôt git local pointant sur `NylenIA/Irminsul` → canonique sans ambiguïté.

## Copies NON canoniques (à ne pas utiliser)

- `<racine locale>/duo-agents-fork` — **fork Duo, interdit par la mission**. Aucune écriture.
- `E:/Bureau/Irminsul-main` — **pas un dépôt git** (snapshot/copie ; source du `RAPPORT_SESSION_2026-06-29.md`). Non canonique, potentiellement périmé.

## Stratégie de branche + arbitrage documenté

- Base choisie : **`main`** (consigne : « ne pas mélanger avec `feat/combat-engine-phase3` », « ne pas modifier la branche principale »).
- **Arbitrage signalé** : `feat/combat-engine-phase3` (PR #3, non fusionnée) est **19 commits en avance** et contient le pont moteur frontend `engine.ts` (+141) et `QuickCalc.tsx` (+318). En basant sur `main`, ces intégrations **ne sont pas présentes** sur la branche redesign.
  - Conséquence : le **câblage des vraies données** (écran pilote) dépend de la fusion de PR #3 dans `main`, OU d'un rebase ultérieur du redesign sur phase3.
  - Le travail de **fondation** (design tokens, shell, design system, audit d'avancement, docs) est **indépendant de la base** et peut avancer dès maintenant sans simuler de données.
- Recommandation : fusionner/rebaser PR #3 avant la phase « écran pilote branché données ». Décision produit ouverte côté propriétaire.
