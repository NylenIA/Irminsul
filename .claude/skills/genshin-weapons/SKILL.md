---
name: Genshin Weapon Allocation
description: Analyse les armes possédées et propose la meilleure répartition réaliste entre les personnages du compte.
argument-hint: "<personnage, type d'arme ou objectif>"
---
Analyse les armes (contexte : $ARGUMENTS).

1. Charge `data/account/current/weapons.json` (armes **scannées** ; le champ `id` Kamera n'est PAS fiable, utilise les ids internes stables). N'invente aucune arme absente.
2. Repère les **armes sous-montées** (niveau << niveau du porteur) et les armes fortes **libres** mal exploitées.
3. Propose une **répartition** par personnage maximisant le compte global, en respectant l'**allocation exclusive** (une arme = un perso à la fois) ; signale les conflits entre équipes d'Abîme.
4. Donne le gain attendu `[CALCUL]` d'un swap/montée de niveau, et le coût (Mora/minerai) selon les matériaux scannés.
5. Sépare `[SCAN]/[CALCUL]/[THEORYCRAFT]`. Vérifie la fraîcheur si tu cites la méta des armes.
