# Backlog Irminsul — tout ce qui a été demandé

Liste de référence tenue à jour à chaque session. Elle reprend **toutes** les
demandes du joueur depuis le début, avec leur état réel. On s'y réfère avant
de commencer quoi que ce soit, pour ne pas partir de travers.

Légende : ✅ fait et vérifié · 🟡 partiel · ⬜ pas commencé

---

## A. Moteur de simulation (priorité actuelle)

| # | Demande | État |
|---|---|---|
| A1 | Ajouter à gcsim **tous** les persos manquants | 🟡 4/11 : Sandrone, Zibai, Illuga, Linnea. Restent Lohen, Nefer, Kachina, Ifa, Jahoda, Prune, + Iansan (déjà via PR commu) |
| A2 | Ajouter les **armes** manquantes | 🟡 2/3 : A Teaspoon of Transcendence, Lightbearing Moonshard. Reste Disaster and Remorse (Lohen) |
| A3 | **Kit COMPLET** pour chaque perso ajouté : multiplicateurs + passifs + constellations + passif d'arme | 🟡 Zibai : passifs ✅, C2 ✅, arme ✅, C1 partielle. Sandrone/Illuga/Linnea : multiplicateurs seuls |
| A4 | Persos **pas encore sortis** (assez d'infos pour calculer la méta) | ⬜ à faire en mode SPÉCULATION séparé |
| A5 | Réaction **Stellar-Conduct** dans le cœur du moteur | ⬜ gcsim connaît Lunar-Charged/Bloom/Crystallize, pas Stellar-Conduct |
| A6 | Afficher aussi le **régime établi** (DPS après la 2ᵉ rotation), pas seulement la moyenne 90 s | ⬜ c'est ce que mesure le compteur en jeu (UGC) |

## B. Équipes et calculs

| # | Demande | État |
|---|---|---|
| B1 | Vrai optimiseur d'équipes, cohérent avec le contenu ET la box | ✅ moteur par archétypes, score explicable |
| B2 | Partir de la **méta réelle**, jamais de combinaisons inventées | 🟡 fait pour Zibai (BiS KQM). À généraliser : liste méta de référence par contenu, validée |
| B3 | Meilleure équipe par contenu + version adaptée si persos manquants | ✅ |
| B4 | Jouable maintenant **et** version « si tu montes / si tu obtiens » | ✅ |
| B5 | **Rotations pré-faites** proposées selon l'équipe détectée | ⬜ les archétypes portent déjà les actions par poste |
| B6 | Rotation qui ressemble à ce qu'on joue vraiment en jeu | ⬜ dépend de B5 et A6 |
| B7 | Pour une équipe créée : dire quoi faire (rotation + rôle de chaque perso) | ⬜ |
| B8 | Ne jamais citer un perso absent de l'équipe affichée | ✅ substitutions appliquées aux textes, alias compris |

## C. Contenus end-game

| # | Demande | État |
|---|---|---|
| C1 | Contenus actuels affichés et maintenus (Abîme, Théâtre, Carnage) | ✅ avec dates et sources |
| C2 | Stratégie adéquate indiquée dans l'app | 🟡 par mode. Par **boss** : ⬜ |
| C3 | **Images** des boss et ennemis à affronter | ⬜ |
| C4 | Filtre des éléments imposés (Théâtre) | ✅ |

## D. Interface

| # | Demande | État |
|---|---|---|
| D1 | Dashboard **utile**, pas un copier-coller d'Équipes | ⬜ |
| D2 | Onglet **builds par perso** (comme dans le jeu : stats, artefacts, armes) | ⬜ |
| D3 | Garder artefacts/stats pour tout calcul, avec interrupteurs **on/off** | ⬜ |
| D4 | **Images** des persos manquants ; fiches des leaks comme Columbina, avec assets non officiels en attendant | ⬜ |
| D5 | Pouvoir choisir **plusieurs modes** pour une équipe créée | 🟡 un seul mode aujourd'hui |
| D6 | Expliquer comment l'app calcule (transparence) | ✅ chaque facteur affiché |

## E. Mises à jour et infrastructure

| # | Demande | État |
|---|---|---|
| E1 | Moteur gcsim toujours à la dernière version, vérifiable | ✅ compilé depuis la source, rebuild quotidien |
| E2 | Méta et contenus mis à jour sans réinstaller | ✅ OTA automatique au démarrage |
| E3 | **Mise à jour de l'app elle-même depuis l'app** (binaire) | ⬜ aujourd'hui : retéléchargement manuel |
| E4 | Liste des persos simulables toujours juste | ✅ générée depuis le moteur compilé |
| E5 | Sauvegarde : code public, données perso dans un dépôt **privé** | ✅ `NylenIA/irminsul-prive` |

## F. Méthode (règles permanentes)

- Toujours partir de la **méta** avant de coder une équipe ; sources datées.
- Ne jamais présenter un **leak** comme confirmé.
- Kit complet obligatoire pour tout perso ajouté (A3).
- Un « build success » ne prouve rien : **vérifier par simulation** avec le
  binaire publié, sur la box réelle.
- Marquer explicitement ce qui est approximé (frames, particules, passifs
  absents) — sous-estimer plutôt que surestimer.

---

## Ordre de travail proposé

1. **A3** — finir les kits (Zibai C1, puis Sandrone, Illuga, Linnea)
2. **A1/A2** — Lohen + son arme, puis les 4★ restants
3. **B5/B6/B7** — rotations pré-faites et lisibles
4. **A6** — régime établi vs moyenne 90 s (pour réconcilier avec le jeu)
5. **D1/D2/D3** — dashboard utile, builds par perso, interrupteurs
6. **C2/C3** — stratégie et images par boss
7. **E3** — mise à jour de l'app depuis l'app
8. **A4/D4** — persos non sortis et leaks, étiquetés SPÉCULATION
