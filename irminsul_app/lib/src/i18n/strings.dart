import "package:flutter/widgets.dart";

/// i18n minimaliste et robuste (FR/EN) — architecture prête à s'étendre.
class L {
  final Locale locale;
  const L(this.locale);

  static const supported = [Locale("fr"), Locale("en")];

  String get code => locale.languageCode;

  String t(String key) => _data[key]?[code] ?? _data[key]?["en"] ?? key;

  static const Map<String, Map<String, String>> _data = {
    "welcomeTitle": {
      "fr": "Bienvenue sur Irminsul",
      "en": "Welcome to Irminsul",
    },
    "welcomeSubtitle": {
      "fr":
          "Ton compagnon de theorycrafting Genshin, en local. Tes données ne quittent jamais ta machine.",
      "en":
          "Your Genshin theorycrafting companion, offline. Your data never leaves your machine.",
    },
    "importGoodTitle": {
      "fr": "Importer un fichier de scan",
      "en": "Import a scan file",
    },
    "importGoodDesc": {
      "fr":
          "Choisis ton .json au format GOOD (Inventory Kamera / Genshin Optimizer).",
      "en":
          "Choose your .json in GOOD format (Inventory Kamera / Genshin Optimizer).",
    },
    "importGoodButton": {"fr": "Choisir un fichier", "en": "Choose a file"},
    "importEnkaTitle": {"fr": "Ou utilise ton UID", "en": "Or use your UID"},
    "importEnkaDesc": {
      "fr":
          "Récupère ta vitrine via Enka.network (les persos affichés dans ta vitrine en jeu).",
      "en":
          "Fetch your showcase via Enka.network (the characters shown in your in-game showcase).",
    },
    "importEnkaHint": {"fr": "ex. 700000001", "en": "e.g. 700000001"},
    "importEnkaButton": {"fr": "Récupérer", "en": "Fetch"},
    "enkaComingSoon": {
      "fr": "Import Enka bientôt disponible (Étape 2).",
      "en": "Enka import coming soon (Step 2).",
    },
    "importError": {"fr": "Import impossible : ", "en": "Import failed: "},
    "greeting": {"fr": "Bonjour, Voyageur", "en": "Hello, Traveler"},
    "dashboardSubtitle": {
      "fr": "Ton compte est prêt.",
      "en": "Your account is ready.",
    },
    "accountImported": {"fr": "Compte importé", "en": "Account imported"},
    "charactersCount": {"fr": "personnages", "en": "characters"},
    "comingSoon": {
      "fr":
          "Bientôt : tes meilleures équipes, classées par mode, avec le DPS et ce qui te manque.",
      "en":
          "Coming soon: your best teams, ranked by mode, with DPS and what you're missing.",
    },
    "changeAccount": {"fr": "Changer de compte", "en": "Change account"},
    "underConstruction": {
      "fr": "En construction — bientôt disponible",
      "en": "Under construction — coming soon",
    },
    "navDashboard": {"fr": "Tableau de bord", "en": "Dashboard"},
    "navCharacters": {"fr": "Mes personnages", "en": "My characters"},
    "navTeams": {"fr": "Équipes", "en": "Teams"},
    "navCompare": {"fr": "Comparateur", "en": "Compare"},
    "navGuides": {"fr": "Guides persos", "en": "Character guides"},
    "navFarm": {"fr": "Que farmer", "en": "What to farm"},
    "navSettings": {"fr": "Réglages", "en": "Settings"},
    "sectionMain": {"fr": "Principal", "en": "Main"},
    "sectionResources": {"fr": "Ressources", "en": "Resources"},
    "settingsTheme": {"fr": "Couleur du thème", "en": "Theme color"},
    "settingsThemeDesc": {
      "fr":
          "Choisis l'ambiance de l'app — Sumeru pour la verdure de Nahida, ou une autre région. Le logo Irminsul garde ses couleurs.",
      "en":
          "Pick the app's mood — Sumeru for Nahida's greenery, or another region. The Irminsul logo keeps its colors.",
    },
    "settingsLanguage": {"fr": "Langue", "en": "Language"},
    "greetingName": {"fr": "Bonjour,", "en": "Hello,"},
    "bestTeamsFor": {
      "fr": "Tes meilleures équipes",
      "en": "Your best teams",
    },
    "modeAbyss": {"fr": "Abîme", "en": "Abyss"},
    "modeTheater": {"fr": "Théâtre", "en": "Theater"},
    "modeOnslaught": {"fr": "Carnage", "en": "Onslaught"},
    "dpsPerRotation": {"fr": "DPS / rotation", "en": "DPS / rotation"},
    "rotationLabel": {"fr": "Rotation", "en": "Rotation"},
    "badgeMeta": {"fr": "MÉTA", "en": "META"},
    "badgeViable": {"fr": "VIABLE", "en": "VIABLE"},
    "badgeLocked": {"fr": "IL TE MANQUE", "en": "MISSING"},
    "missingPrefix": {"fr": "Il te manque", "en": "You're missing"},
    "missingSuffix": {
      "fr": "de DPS en plus. On ne bricole pas de team à tout prix.",
      "en": "more DPS. We never botch a team just to fill slots.",
    },
    "demoDataNote": {
      "fr":
          "Données de démonstration (theorycraft indicatif) — moteur gcsim et BDD méta curée à venir.",
      "en":
          "Demo data (indicative theorycraft) — gcsim engine and curated meta DB coming.",
    },
    "enkaLoading": {"fr": "Récupération…", "en": "Fetching…"},
    "guidesSubtitle": {
      "fr": "La Gazette de Teyvat — builds, priorités et matériaux, vérifiés.",
      "en": "The Teyvat Gazette — builds, priorities and materials, verified.",
    },
    "curatedNote": {
      "fr":
          "Fiches curées (démo) — matériaux vérifiés dans les données du jeu ; builds = standards communautaires. BDD complète via la synchro.",
      "en":
          "Curated sheets (demo) — materials verified against game data; builds follow community standards. Full DB comes with sync.",
    },
    "back": {"fr": "Retour", "en": "Back"},
    "sectionTalents": {"fr": "Priorité d'aptitudes", "en": "Talent priority"},
    "sectionWeapons": {"fr": "Armes recommandées", "en": "Recommended weapons"},
    "sectionArtifacts": {"fr": "Artefacts", "en": "Artifacts"},
    "sectionConstellations": {
      "fr": "Constellations clés",
      "en": "Key constellations",
    },
    "sectionMaterials": {"fr": "Matériaux", "en": "Materials"},
    "artifactSet": {"fr": "Set", "en": "Set"},
    "artifactSands": {"fr": "Sablier", "en": "Sands"},
    "artifactGoblet": {"fr": "Coupe", "en": "Goblet"},
    "artifactCirclet": {"fr": "Diadème", "en": "Circlet"},
    "artifactSubs": {"fr": "Sous-stats", "en": "Substats"},
    "matGems": {"fr": "Gemmes", "en": "Gems"},
    "matBoss": {"fr": "Boss", "en": "Boss"},
    "matLocal": {"fr": "Spécialité locale", "en": "Local specialty"},
    "matCommon": {"fr": "Communs", "en": "Common"},
    "matTalent": {"fr": "Livres d'aptitude", "en": "Talent books"},
    "matWeekly": {"fr": "Boss hebdo", "en": "Weekly boss"},
    "syncUpToDate": {"fr": "Données à jour", "en": "Data up to date"},
    "syncUpdate": {"fr": "Màj méta dispo :", "en": "Meta update available:"},
    "syncOffline": {"fr": "Hors-ligne", "en": "Offline"},
    "searchHint": {"fr": "Rechercher un personnage…", "en": "Search a character…"},
    "tabBuild": {"fr": "Build", "en": "Build"},
    "tabTalents": {"fr": "Aptitudes", "en": "Talents"},
    "tabCons": {"fr": "Constellations", "en": "Constellations"},
    "tabMats": {"fr": "Matériaux", "en": "Materials"},
    "buildSoon": {
      "fr":
          "Build curé à venir via la synchro méta. Les données du jeu (aptitudes, constellations, matériaux) sont déjà complètes ci-contre.",
      "en":
          "Curated build coming via meta sync. Game data (talents, constellations, materials) is already complete here.",
    },
    "matAsc": {"fr": "Élévation du personnage", "en": "Character ascension"},
    "matTal": {"fr": "Amélioration des aptitudes", "en": "Talent upgrades"},
    "archonBadge": {"fr": "Archon", "en": "Archon"},
    "settingsTraveler": {"fr": "Voyageur·se", "en": "Traveler"},
    "settingsTravelerDesc": {
      "fr":
          "Choisis ton jumeau : c'est lui ou elle qui apparaît dans la Gazette, avec toutes ses variantes d'élément.",
      "en":
          "Pick your twin: they appear in the Gazette with all their element variants.",
    },
    "bestMetaBuild": {
      "fr": "Meilleur build selon la méta actuelle",
      "en": "Best build in the current meta",
    },
    "teamsSubtitle": {
      "fr":
          "Les équipes méta croisées avec TA box — jamais de bricolage : un slot manquant est dit manquant.",
      "en":
          "Meta teams crossed with YOUR box — never botched: a missing slot is called missing.",
    },
    "teamsNoBox": {
      "fr": "Importe ta box pour commencer",
      "en": "Import your box to get started",
    },
    "teamsNoBoxDesc": {
      "fr":
          "Le Team Builder a besoin de ton fichier GOOD (Inventory Kamera / Genshin Optimizer) : persos, constellations, niveaux et artefacts. L'import Enka (vitrine) ne suffit pas pour le croisement complet.",
      "en":
          "The Team Builder needs your GOOD file (Inventory Kamera / Genshin Optimizer): characters, constellations, levels and artifacts. Enka (showcase) is not enough for full matching.",
    },
    "teamsNoBoxCta": {"fr": "Importer mon fichier", "en": "Import my file"},
    "teamsCrossedWith": {"fr": "Croisé avec", "en": "Crossed with"},
    "teamsComplete": {"fr": "COMPLÈTE", "en": "COMPLETE"},
    "teamsMissingPrefix": {"fr": "IL TE MANQUE", "en": "MISSING"},
    "teamsMissingChar": {"fr": "manquant", "en": "missing"},
    "teamsAlt": {"fr": "ALT", "en": "ALT"},
    "teamsRotation": {"fr": "Rotation & combos", "en": "Rotation & combos"},
    "teamsErEst": {"fr": "recharge calculée", "en": "computed ER"},
    "teamsErAdvised": {"fr": "· conseillé", "en": "· advised"},
    "teamsErNote": {
      "fr": "(artefacts + arme, depuis ton GOOD)",
      "en": "(artifacts + weapon, from your GOOD)",
    },
    "teamsSuggestFor": {"fr": "en attendant :", "en": "meanwhile:"},
    "teamsNoSuggest": {
      "fr": "aucun remplaçant valable dans ta box",
      "en": "no valid replacement in your box",
    },
    "teamsToBuild": {"fr": "à monter", "en": "needs building"},
    "teamsDemoNote": {
      "fr":
          "BDD méta de démonstration (5 équipes curées) — elle s'étoffera via la synchro. Le croisement avec ta box, lui, est réel.",
      "en":
          "Demo meta DB (5 curated teams) — it will grow via sync. The matching with your box is real.",
    },
    "leaksSection": {
      "fr": "Leaks · non confirmés",
      "en": "Leaks · unconfirmed",
    },
    "leakBadge": {"fr": "LEAK", "en": "LEAK"},
    "leakExpected": {"fr": "Attendue", "en": "Expected"},
    "leakScore": {"fr": "Fiabilité estimée", "en": "Estimated reliability"},
    "leakSources": {"fr": "Sources publiques", "en": "Public sources"},
    "leakUpdated": {"fr": "Dernière mise à jour :", "en": "Last updated:"},
    "gameDataNote": {
      "fr":
          "Données du jeu (genshin-db, FR officiel) — noms et descriptions exacts, 120 personnages.",
      "en":
          "Game data (genshin-db, official FR) — exact names and descriptions, 120 characters.",
    },
  };
}
