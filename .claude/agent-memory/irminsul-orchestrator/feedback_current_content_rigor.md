---
name: current-content-rigor
description: Contenus de fin de jeu (Abîme/Théâtre/Carnage) — vérifier la période EN COURS avec ses dates avant de l'afficher comme actuelle
metadata:
  type: feedback
---

Avant d'afficher ou d'affirmer un **contenu de fin de jeu actuel** (bénédiction
d'Abîme, éléments du Théâtre imaginaire, boss du Carnage stygien), vérifier la
**période en cours à la date du jour** sur une source datée, et stocker les
**bornes du cycle** (`from`/`to` ISO) plutôt qu'une phrase figée.

**Why:** le 2026-07-27 j'avais embarqué dans l'app la saison de Théâtre **du
1ᵉʳ août** (Cryo·Hydro·Électro) en la présentant comme « contenu actuel », alors
que la saison en cours était la 25 (1ᵉʳ–30 juillet, **Pyro·Cryo·Électro**).
Conséquence : les 3 équipes proposées pour ce mode étaient **littéralement
injouables** (Hydro/Dendro interdits). Même passage : la stratégie du Carnage
avait été *devinée* (« Supraconducteur ») au lieu d'être sourcée (en vrai :
drones Hydro à détruire, bouclier qui prend +300 % des réactions Lunaires,
piliers Nightsoul).

**How to apply:**
- Le Théâtre change **chaque mois** (saison du 1er au ~30) ; l'Abîme le 1er et
  le 16 ; le Carnage suit le patch. Toujours recalculer « en cours / à venir /
  terminé » à partir des dates, jamais à partir d'un texte.
- Ne pas confondre une **preview / donnée datamine** du cycle suivant avec le
  cycle en cours — et si c'est du leak, l'étiqueter (cf. politique leaks).
- Côté app : `irminsul_app/tool/update_meta_db.py` porte les contenus datés +
  `source` par mode ; relancer à chaque cycle, la synchro OTA fait le reste
  (pas besoin de rebuild). Vérifier aussi que les équipes proposées respectent
  la **restriction d'éléments** de la saison.
- Se rappeler que l'utilisateur joue ces contenus : une reco injouable est pire
  qu'une absence de reco (cf. [[feedback-meta-research-rigor]], [[user-profile]]).
