---
name: Genshin Artifact Optimizer
description: Analyse, classe et optimise les artéfacts réellement présents dans le compte (équipés et libres).
argument-hint: "<personnage, set ou objectif>"
---
Analyse les artéfacts (contexte : $ARGUMENTS).

1. Charge `data/account/current/artifacts.json` (artéfacts **scannés**, équipés + libres). N'invente aucun artéfact absent.
2. Classe par **crit value** et pertinence de main stat/set pour la cible demandée ; distingue artéfacts **libres** (`location` absente) et **équipés** (avec le perso porteur).
3. Pour un perso : propose le meilleur set réalisable avec le stock, les pièces exactes (ids internes stables) et le gain estimé `[CALCUL]` vs build actuel.
4. Respecte l'**allocation exclusive** : ne propose pas une pièce déjà nécessaire ailleurs sans le signaler.
5. Signale les sets à **dédoubler** pour les deux équipes d'Abîme. Sépare `[SCAN]/[CALCUL]/[THEORYCRAFT]`.
