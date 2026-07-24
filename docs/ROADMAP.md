# Irminsul — Feuille de route (cahier des charges adopté)

> Source : cahier des charges **v7** fourni par l'utilisateur (2026-07-24), adopté
> comme feuille de route **adaptable**. Ce fichier vit sur GitHub (versionné).
> Vision produit : voir [VISION.md](VISION.md). Ajustements honnêtes du Tech Lead : **Annexe A**.

---

## Rôle & mode de travail

- **Tech Lead 100 % autonome sur la technique.** L'utilisateur ne code pas → je
  prends les décisions techniques (librairies, archi, état, DB) et j'avance, je
  corrige mes erreurs moi-même, je vulgarise mes comptes-rendus (UI/UX, pas code brut).
- **Collaboration sur produit & design.** *(amendement Tech Lead — cf. Annexe A.0)*
- **CI/CD comme boucle de test :** à chaque étape majeure, **GitHub Actions** produit
  un exécutable (`.exe` Windows) que l'utilisateur télécharge et teste visuellement.

## Règles d'or (méta, rotations, connecteur IA)

1. **Teams méta & viables, sans concession.** Uniquement des équipes réellement
   viables depuis la box. Jamais de bricolage. Si impossible → *« Il te manque
   [Perso X] pour débloquer une équipe méta sur cet archétype. »*
2. **Rotations & combos par équipe (indispensable) :** ordre de passage, séquence
   exacte (E → Q → swap), combos & cancels (ex. N2C jump cancel), **ER check** (alerte
   si la recharge réelle du joueur ne tient pas la boucle).
3. **Bring-Your-Own-AI :** app autonome, **zéro coût LLM** ; expose son état local
   (roster, DPS, builds) via un **connecteur type MCP** pour brancher son propre LLM.

## Data, sources, veille & moteur de simulation

- **Veille méta / patch sync (OTA) :** au démarrage, vérifier la version active et,
  si nouveau patch, télécharger les nouveaux JSON méta sans réinstaller l'app.
- **Sources :** data brute & fiches → `ambr.top`, `HomDgcat`, `GenshinData`/`GenshinDb`/
  `HoneyHunter` ; standards méta → **KQM** + **gcsim DB** ; import roster → **Enka.network**
  + parseur **GOOD**.
- **Fiches « Gazette de Teyvat » :** rôles, priorité aptitudes, armes, artefacts BiS,
  constellations clés, matériaux.
- **Architecture données :** i18n **FR/EN** dès J1 ; **séparation code/data** (OTA) ;
  **mock data** initial (3-4 persos) pour le POC.
- **gcsim :** binaire Go embarqué (FFI / isolate / process). **Templates dynamiques** :
  injecter les stats réelles du joueur (GOOD/Enka) dans des scripts gcsim pré-écrits
  par équipe méta.

## Expérience & fonctionnalités exclusives

1. **Onboarding premium** (import GOOD ou UID Enka).
2. **Impact de bannière (« Should You Pull ? »)** : score de valeur d'un perso pour la box.
3. **Timeline de rotation interactive** (Gantt : temps de terrain, uptime des buffs).
4. **Build Cards** : export image HD (façon Enka).
5. **Cache agressif** des images (fluidité, hors-ligne partiel).

## Stack technique

- **UI :** Flutter multiplateforme.
- **Design :** type *Helios Investments* (sombre profond, glassmorphism léger, cartes
  aérées, accents par élément Genshin).
- **Données joueur :** strictement **locales** (privacy by design).
- *(Décisions Tech Lead : état = **Riverpod** ; DB locale = **Isar** ; nav = **go_router** ;
  build = **GitHub Actions**.)*

## Plan d'action (roadmap)

- **Étape 1 — Socle, CI/CD, i18n, Onboarding :** Flutter + GitHub Actions, structure
  Riverpod/i18n, cache, écran d'import (GOOD/Enka).
- **Étape 2 — Mock data, Veille/Patch check, Fiches persos (UI Helios) :** dashboard,
  vérif de version, BDD JSON statique, vue « Gazette » + connecteurs (Ambr/Enka).
- **Étape 3 — Team Builder méta & rotations :** croisement box × BDD méta (KQM),
  alertes ER, combos, personnages manquants.
- **Étape 4 — Pont gcsim & templates :** intégration gcsim, générateur d'Action Lists
  sur builds réels, Timeline visuelle.
- **Étape 5 — Premium :** « Should you pull », Build Cards, connecteur BYO-AI.

---

## Étape 4.3 — sous-étapes (validées une par une par l'utilisateur, 2026-07-25)

- **4.3.1 — Moteur & liberté** ✅ : gcsim compilé depuis la DERNIÈRE source à
  chaque build CI (persos plus récents que la release, ex. Columbina) + version
  du moteur affichée dans l'app · fix « 0 s de terrain » (field_time déjà en
  secondes) · créateur : **ATQ ×1 à ×8** au choix (- / +) · astuce anti-piège
  « ulti en début de rotation = 0 énergie ».
  Constat vérifié : Zibai/Sandrone/Iansan/Varka/Nefer **pas implémentés** dans
  gcsim même à HEAD (pas une question de version — travail de l'équipe gcsim).
- **4.3.2 — Templates partout + dashboard réel + contenus actuels** ⏳
  (attend validation) — périmètre étendu le 2026-07-25 sur demande :
  * rotations gcsim validées pour les 15 équipes — **optimales mais jouables
    à la main** ;
  * DPS de démo du dashboard remplacés par les résultats simulés réels (cache) ;
  * **équipes créées sauvegardables dans « Équipes »** avec un mode
    (Abîme / Théâtre / Carnage) ;
  * **contenus ACTUELS du patch** affichés et maintenus : boss/bénédiction de
    l'Abîme, éléments du Théâtre, boss du Carnage — avec la **stratégie
    adéquate** indiquée dans l'app ;
  * meilleure team par contenu, et si persos manquants → **version adaptée à
    la box** (le moteur de substitution existe déjà : slots alts/pool +
    rotations auto-adaptées).
- **4.3.3 — Persos absents & leaks** ⏳ (attend validation) : calcul théorique
  étiqueté SPÉCULATION pour les kits leakés documentés (Odette V3) via nos
  propres formules ; suivi auto des nouveaux persos ajoutés à gcsim.

## Annexe A — Ajustements du Tech Lead (réalité de terrain)

> Je garde **tout** le cahier des charges. Ces points sont des **franchises** pour
> qu'on avance sans mauvaise surprise. Rien n'est retiré — c'est du cadrage.

- **A.0 — Autopilote technique, oui ; produit/design, on collabore.** Je ne t'embête
  pas avec les choix de librairies. Mais l'app est la tienne et tu as l'œil : je
  continue à te **montrer le design et les décisions produit** (ça nous a déjà évité
  de partir de travers).
- **A.1 — gcsim : PC d'abord.** Le DPS grade-simu via gcsim est **propre sur desktop**.
  Sur **mobile**, lancer un binaire Go est un vrai casse-tête (surtout iOS) → **v1
  desktop**, mobile plus tard. Flutter garde la porte ouverte.
- **A.2 — Pas d'API patch officielle HoYo.** La « détection de patch » se fait via les
  **sources communautaires** (ambr/enka) qui s'updatent à chaque version. Fiable, mais
  communautaire.
- **A.3 — Veille « automatique » ≠ 100 % magique.** On automatise la **synchro data**,
  mais la **BDD des teams méta** et les **scripts de rotation gcsim** demandent une
  **curation à chaque patch** (vrai travail récurrent, assumé).
- **A.4 — Leaks / bêta (HomDgcat) : toujours étiquetés.** On peut les intégrer, mais
  **jamais** présentés comme méta confirmée — libellés **LEAK/SPÉCULATION**, séparés du
  live. Règle dure du projet.
- **A.5 — Licences & ToS.** Images/données (ambr, Enka, Honey, GenshinData…) : respect
  des conditions d'usage, cache poli, attribution. Distribution publique des assets à
  vérifier.
- **A.6 — On ship par tranches.** Chaque étape produit un `.exe` testable. On ne lance
  pas les 5 étapes en parallèle (c'est ce qui a coulé la version précédente).

## Annexe B — Comment on teste sans que tu compiles

1. Je développe et je **pousse sur GitHub**.
2. **GitHub Actions** compile un **`.exe` Windows** à chaque étape.
3. Tu le **télécharges depuis l'onglet Releases/Actions** et tu testes visuellement.
4. Tu me dis ce qui va / ne va pas → j'itère. Rien de lourd sur ton PC.
