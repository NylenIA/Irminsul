# Irminsul — Vision de l'app (document vivant)

> **But de ce doc :** poser noir sur blanc ce qu'on veut construire, **avant de coder**.
> Il évolue au fil des idées. On le modifie à chaque fois qu'un truc se précise.
> Légende de statut : ✅ décidé · 🟡 à préciser · 🟠 gros / à étaler · 🔴 à ne pas construire · ❓ ton avis attendu.

Dernière mise à jour : 2026-07-24

---

## 1. En une phrase

Un **théorycrafteur dans une app** : il prend **ton compte Genshin**, connaît la
**méta du moment**, et te dit **tes meilleures équipes + leur DPS**, par mode de
fin de jeu — automatiquement, sur tes vrais builds. ✅

## 2. Pour qui

- Toi d'abord (joueur avancé, calé méta, exigeant sur la rigueur).
- Puis **n'importe qui** : installable facilement, gratuit. ✅

## 3. Le moment magique 🟡

Proposition à valider : un **tableau de bord** —
« Voici tes **meilleures équipes** pour le patch actuel, classées **par mode**
(Abîme / Théâtre / Carnage), chacune avec **son DPS** et **ce qui te manque**. »

❓ C'est bien ça le premier écran, ou tu vois autre chose en premier ?

## 4. Ce que l'app fait

### 4.1 Le cœur : reco d'équipes par mode ✅
- **Ta** meilleure team (montable avec ton roster) **ET** la meilleure du jeu
  **+ ce qui te manque** pour l'avoir. ✅
- **Règle de qualité (actée 2026-07-24)** : on ne propose **QUE** des teams
  **méta et viables**. On ne bricole **jamais** une team « à tout prix » pour
  remplir 4 slots. Si le roster ne permet pas une bonne team, l'app le **dit** :
  « il te manque **X** pour une team fonctionnelle ». ✅
- Décliné **par mode** (chacun récompense des choses différentes) :
  - **Abîme (Spiral Abyss)** — 2 équipes, course au temps / check de DPS. 🟡
  - **Théâtre (Imaginarium Theater)** — beaucoup de persos, contraintes d'éléments
    → valorise la **largeur du roster**. 🟡
  - **Carnage (mode boss / onslaught)** — une équipe qui **tient et burst** sur un
    boss unique. 🟡 *(nom exact à confirmer)*

### 4.2 DPS d'équipe ✅
- **DPS brut** + **capacité à clear** le mode visé (pas juste un gros chiffre). ✅

### 4.3 Builds (artefacts / armes) 🟡
- Conseils « quoi farmer / équiper pour gagner X% ». Inclus dans la vision. ✅

### 4.4 La grande vision — le catalogue complet (avec réalité de terrain)

> Tout ce que tu as demandé est **gardé ici**. Le tag dit à quel point c'est
> réaliste à faire **bien** — pour choisir l'ordre en connaissance de cause.

| Fonction souhaitée | Réalité | Note honnête |
|---|---|---|
| **Theorycrafter** (teams / DPS / builds sur ton compte) | ✅ **Cœur, faisable** | Notre différenciant. On y met le paquet. |
| **Fiches persos + matériaux** d'ascension (façon la Gazette) | ✅ **Faisable en couche** | Données à curer + tenir à jour chaque patch. |
| **Optim artefacts** (façon Genshin Optimizer) | 🟠 **Faisable, gros** | GO = projet mûr d'une équipe. Version focalisée, par étapes. |
| **« Boosté à l'IA » = branche TON IA** | ✅ **Malin, gratuit pour nous** | Pas de LLM payé par l'app. On expose un **connecteur** : qui a déjà une IA la **relie** pour suggérer teams/méta, faire la **veille**, etc. Zéro coût de notre côté ; l'app marche **sans** IA. |
| **Scanner le compte** façon Inventory Kamera (OCR écran) | 🟠 **Gros projet séparé** | OCR **local Windows** → colle mal avec natif-multiplateforme + cloud. **Alternative** : importer le fichier **GOOD** que Inventory Kamera / GO produisent déjà (1 clic), ou **Enka** via UID. |
| **Carte interactive de Teyvat** | 🔴 **À ne pas recréer** | Imagerie + milliers de marqueurs + maj chaque patch + conditions Hoyolab. **Alternative** : lien vers une carte existante. |

**Principe** : le doc garde **tout** le rêve. L'app se construit **une brique
excellente à la fois**.

### 4.5 Connecte ton IA (bring-your-own-AI) ✅
- L'app expose ses **données et actions** (roster, builds, teams, DPS, méta) pour
  qu'une **IA externe — celle de l'utilisateur —** puisse suggérer des équipes,
  commenter la méta, faire de la **veille** (patchs, bannières, shifts de méta).
- **L'app fonctionne à 100 % sans IA.** L'IA est un **plus optionnel**, branché par
  qui le veut. → aucun coût LLM à notre charge, cohérent avec « gratuit ». ✅
- *(Techniquement proche d'une interface type MCP — à cadrer plus tard.)* 🟡

## 5. Niveau d'exigence ✅

- **Précis, grade simulation.** On vise du **gcsim** (référence de la commu),
  embarqué comme moteur natif.
- Toujours afficher les **hypothèses** (rotation, ennemi, uptime). ✅
- Séparer **plafond théorique** vs **performance réelle**. ✅

## 6. Design & feeling 🟡 (direction posée le 2026-07-24)

**Référence maîtresse** : dashboard type *Helios Investments* (sombre,
glassmorphism, cartes arrondies, dégradé **violet/rose** en accent, **sidebar** de
navigation, graphes épurés et animés) — **version Genshin**. *(réfs Pinterest fournies)*

- **Ambiance** : ✅ **mélange** « gamer/Genshin » **et** « outil pro épuré ».
  → base sobre et pro **rehaussée** de touches Genshin (couleurs par élément en
  accent, icônes/illustrations persos).
- **Structure** : sidebar + cartes (comme la réf). ✅
- **Accent couleur** : dégradé violet/rose. 🟡 *(décliner par élément ?)*
- **Densité** : riche mais **respirant** (cartes séparées, pas de mur d'infos). 🟡
- **Icônes / illus** : officielles Genshin (persos/éléments/armes). 🟡 *(licence à vérifier pour distribution publique)*
- **Détails “fini”** : transitions douces, feedback au clic, graphes animés. 🟡
- **Première maquette** : `docs/mockups/theorycrafter-dashboard.html` (2026-07-24). 🟡

## 7. Ordre de construction (proposition 🟡)

- **v1 — la colonne, mais finie et belle** : import compte → tes persos (vrais
  builds) → **meilleures teams méta par mode + DPS chiffré + ce qui te manque**.
- **v2 — la rigueur** : DPS **grade gcsim** pour ta team exacte (rotations).
- **v3 — les couches** : fiches persos+matériaux, puis optim artefacts.

❓ Ça te va comme ordre ?

## 8. Technique (décisions)

- **Vrai app native** (pas de web, pas de webview). ✅
- **Flutter** (PC d'abord, téléphone plus tard). ✅ *(stack : Riverpod, Isar, go_router, GitHub Actions → .exe)*
- **Moteur de simulation : gcsim** embarqué. ✅
- **Gratuit**, code sur **GitHub**, installeur via **GitHub Releases**. ✅
- **Dev + build dans le cloud** (Codespaces + Actions) → rien de lourd sur ton PC. ✅
- **Données privées** : ton compte reste sur ta machine. ✅
- **Import du compte** : via fichier **GOOD** (Inventory Kamera / GO) ou **Enka**.
  *(scanner OCR maison = plus tard, si un jour — cf. §4.4)* ✅
- **Connecteur IA (bring-your-own-AI)** : l'app expose données/actions pour une IA
  externe ; marche **à 100 % sans IA** (cf. §4.5). ✅
- **Réutilisable de l'existant** : formules de dégâts/réactions (testées), logique
  d'import GOOD, connaissance méta. Le reste est reconstruit. 🟡

## 9. Ce qu'on garde / ce qu'on jette (à trancher) 🟡

- **Garder** : le savoir (formules, modèles de données, tests comme référence).
- **Jeter** : Tauri, serveur Next, sidecar Python en l'état, UI actuelle.
- **Repo** : neuf, ou on transforme l'existant ? ❓

## 10. Questions ouvertes (liste vivante)

1. **Brique n°1** : la seule chose que l'app doit faire parfaitement d'abord. ❓
   *(pressenti : le theorycrafter / team builder)*
2. Le premier écran exact (§3). ❓
3. ~~Ce que « boosté à l'IA » veut dire~~ → **résolu** : connecteur « branche ton
   IA », zéro LLM payé par l'app (§4.5). ✅
4. D'où vient la **donnée méta** + les fiches persos (source + maj par patch). 🟡
5. Nom exact et règles du mode « Carnage ». 🟡
6. Nom / identité visuelle (on garde « Irminsul » ?). ❓

## 11. Journal des décisions

- **2026-07-24** — Pivot : abandon de l'app web/Tauri. Cap sur un **vrai app natif**,
  gratuit, code+build **cloud** (GitHub), moteur **gcsim**, rigueur **grade simu**.
  Méthode : **doc d'abord, code ensuite**.
- **2026-07-24** — Design : **dashboard sombre glassmorphism (réf Helios) + touches
  Genshin**, mélange gamer/pro. Vision élargie (scanner, optimizer-IA, carte, guides)
  capturée au **§4.4** → cœur = **theorycrafter** ; import via fichier existant (pas
  d'OCR maison en v1) ; carte non recréée.
- **2026-07-24** — Règles produit : (1) team builder ne propose **que des teams méta
  et viables**, sinon dit « il te manque X » ; (2) **« IA » = connecteur pour l'IA de
  l'utilisateur** (BYO-AI), pas de LLM payé par l'app. Première **maquette** du
  dashboard créée.
- **2026-07-24** — **Cahier des charges v7** adopté comme feuille de route →
  [ROADMAP.md](ROADMAP.md) (5 étapes). Stack actée : **Flutter + Riverpod + Isar +
  go_router + GitHub Actions (build .exe testable)**. Rôle : autopilote **technique**,
  collaboration **produit/design**. Flags honnêtes : gcsim **desktop d'abord** ; pas
  d'API patch officielle ; veille = synchro auto **mais** curation méta/gcsim par
  patch ; **leaks toujours étiquetés**. Rotations + ER-check ajoutés au cœur.
  Prochaine action : **Étape 1** (socle + CI/CD + onboarding).
