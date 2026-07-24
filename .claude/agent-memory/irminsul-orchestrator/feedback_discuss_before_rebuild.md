---
name: discuss-before-big-rebuilds
description: Décisions produit/archi majeures — cadrer et discuter (spec d'abord) avant de foncer dans le code
metadata:
  type: feedback
---

Pour toute décision **produit ou architecture majeure** (refonte, « repartir de
zéro », choix de stack), **discuter et écrire une spec courte d'abord** ; ne pas
enchaîner directement sur du code.

**Why:** le 2026-07-24, après une longue session où j'ai empilé builds et
correctifs, l'utilisateur a constaté que le résultat ne correspondait pas du tout
à ce qu'il voulait (« je ne voulais pas une app comme ça »). Il a explicitement
demandé qu'on **discute pour que je comprenne son besoin réel** avant de
reconstruire, en référence aux méthodes spec-driven (PRD + PLAN + DESIGN).

**How to apply:** face à un pivot ou une ambiguïté produit, reformuler la vision,
poser 3-4 questions ciblées, proposer une spec à valider — et n'ouvrir l'éditeur
qu'une fois l'accord obtenu. Vaut surtout pour Irminsul (cf. [[product-vision-theorycrafter-app]]).
Ne bloque pas les petites tâches d'exécution claires, où [[proactive-improvements]] s'applique.
