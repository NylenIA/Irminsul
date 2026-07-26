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
          "DPS en vert = simulation gcsim sur TA box. DPS grisé = même rotation simulée sur une box standard (Nv 90, talents 9, Favonius, artefacts 5★ génériques) : ça sert à COMPARER les équipes entre elles, pas à prévoir tes chiffres.",
      "en":
          "Green DPS = gcsim simulation on YOUR box. Greyed DPS = same rotation simulated on a standard box (Lv 90, talents 9, Favonius, generic 5★ artifacts): use it to COMPARE teams, not to predict your numbers.",
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
    "syncApply": {
      "fr": "Cliquer pour télécharger la nouvelle méta",
      "en": "Click to download the new meta",
    },
    "syncApplied": {
      "fr": "Méta mise à jour — équipes et contenus rafraîchis",
      "en": "Meta updated — teams and content refreshed",
    },
    "syncFailed": {
      "fr": "Mise à jour impossible (hors-ligne ou données invalides) — rien n'a changé",
      "en": "Update failed (offline or invalid data) — nothing changed",
    },
    "syncSourceOta": {"fr": "téléchargée", "en": "downloaded"},
    "syncUnreachable": {
      "fr": "Source méta inaccessible (dépôt privé) — données du build",
      "en": "Meta source unreachable (private repo) — build data",
    },
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
    "dashAlignedWith": {
      "fr": "à jour sur la version",
      "en": "aligned with version",
    },
    "creatorOpen": {"fr": "Créer ma team", "en": "Create my team"},
    "creatorTitle": {"fr": "Créer ma team", "en": "Create my team"},
    "creatorSubtitle": {
      "fr":
          "Choisis 4 personnages de TA box, construis ta rotation, puis simule le vrai DPS avec gcsim.",
      "en":
          "Pick 4 characters from YOUR box, build your rotation, then simulate the real DPS with gcsim.",
    },
    "creatorStep1": {
      "fr": "Choisis 4 personnages",
      "en": "Pick 4 characters",
    },
    "creatorStep2": {
      "fr": "Construis ta rotation (sélectionne un perso, ajoute ses actions)",
      "en": "Build your rotation (select a character, add their actions)",
    },
    "creatorStep3": {
      "fr": "Nomme, simule, sauvegarde",
      "en": "Name, simulate, save",
    },
    "creatorSaved": {"fr": "Mes équipes créées", "en": "My created teams"},
    "creatorDefaultName": {"fr": "Ma team", "en": "My team"},
    "creatorNameHint": {"fr": "Nom de la team…", "en": "Team name…"},
    "creatorSave": {"fr": "Sauvegarder la team", "en": "Save team"},
    "creatorNoSteps": {
      "fr":
          "Aucune étape — sélectionne un perso ci-dessus puis clique E, Q, ATQ ou CHARGÉE.",
      "en":
          "No steps yet — select a character above then tap E, Q, ATK or CHARGED.",
    },
    "creatorActSkill": {"fr": "Compétence (E)", "en": "Skill (E)"},
    "creatorActBurst": {"fr": "Ultime (Q)", "en": "Burst (Q)"},
    "creatorActAttack": {
      "fr": "Attaques normales",
      "en": "Normal attacks",
    },
    "creatorActAttackN": {
      "fr": "attaque(s) normale(s)",
      "en": "normal attack(s)",
    },
    "creatorActCharge": {"fr": "Attaque chargée", "en": "Charged attack"},
    "creatorTipBurstFirst": {
      "fr":
          "Astuce : les ultis démarrent à 0 énergie. Commence ta rotation par des compétences (E) pour charger, sinon la simulation attend dans le vide.",
      "en":
          "Tip: bursts start at 0 energy. Open your rotation with skills (E) to charge up, otherwise the simulation stalls waiting.",
    },
    "simAdapted": {
      "fr": "Rotation adaptée à ta box :",
      "en": "Rotation adapted to your box:",
    },
    "simEngineVersion": {"fr": "Moteur embarqué", "en": "Bundled engine"},
    "simEngineBuiltFromSource": {
      "fr": "compilé depuis la dernière source à chaque build",
      "en": "built from latest source on every build",
    },
    "creatorActDash": {
      "fr": "Dash (annulation d'animation)",
      "en": "Dash (animation cancel)",
    },
    "creatorActJump": {
      "fr": "Saut (annulation d'animation)",
      "en": "Jump (animation cancel)",
    },
    "settingsEngine": {
      "fr": "Moteur de simulation",
      "en": "Simulation engine",
    },
    "settingsEngineDesc": {
      "fr":
          "Irminsul compile gcsim depuis sa source à chaque build — tu as donc les correctifs et les nouveaux personnages avant même les versions publiées.",
      "en":
          "Irminsul builds gcsim from source on every build — you get fixes and new characters even before published releases.",
    },
    "engineUpToDate": {
      "fr": "À jour (plus récent que la dernière version publiée)",
      "en": "Up to date (newer than the latest published release)",
    },
    "engineOutdated": {
      "fr": "Une version plus récente existe — relance un build",
      "en": "A newer version exists — trigger a new build",
    },
    "engineOffline": {
      "fr": "Vérification impossible (hors-ligne)",
      "en": "Check unavailable (offline)",
    },
    "engineLocalDev": {
      "fr": "Build local (non compilé par la CI)",
      "en": "Local build (not built by CI)",
    },
    "engineBuild": {"fr": "Moteur embarqué", "en": "Bundled engine"},
    "engineLatestRelease": {
      "fr": "Dernière version publiée",
      "en": "Latest published release",
    },
    "engineExtras": {
      "fr": "Persos ajoutés par nous",
      "en": "Characters we added",
    },
    "engineDaily": {
      "fr":
          "gcsim est un moteur open-source : ce sont des joueurs qui codent chaque personnage et corrigent les formules. Chaque nuit (06 h 30 UTC), la CI recompile l'app à partir de leur code du jour — tu récupères donc leurs correctifs et leurs nouveaux personnages sans rien télécharger toi-même, avant même qu'ils publient une version officielle. Un personnage qu'ils n'ont pas encore codé reste absent : c'est pour ça que nous en ajoutons nous-mêmes (ci-dessus).",
      "en":
          "gcsim is open source: players code each character and fix the formulas. Every night (06:30 UTC) CI rebuilds the app from their latest code — you get their fixes and new characters without downloading anything, even before they cut a release. A character they haven't coded yet stays missing: that's why we add some ourselves (above).",
    },
    "simEnergyTitle": {
      "fr": "Ton DPS est sous-estimé : des ultimes n'ont pas pu être lancés",
      "en": "Your DPS is underestimated: some bursts could not be cast",
    },
    "simEnergyBurstFail": {
      "fr": "ultime impossible (énergie insuffisante)",
      "en": "burst impossible (not enough energy)",
    },
    "simEnergyAdvice": {
      "fr":
          "Pendant ces tentatives, la simulation ATTEND sur ce personnage : le temps de terrain est gâché et le DPS chute. Retire son Q de la rotation, espace-le, ou monte sa recharge d'énergie — puis relance.",
      "en":
          "During those attempts the simulation WAITS on that character: field time is wasted and DPS drops. Remove their burst from the rotation, space it out, or raise their Energy Recharge — then run again.",
    },
    "simBreakdown": {
      "fr": "Détail par personnage",
      "en": "Per-character breakdown",
    },
    "simFieldTime": {"fr": "de terrain", "en": "on field"},
    "simUnsupported": {
      "fr": "Pas encore simulable — le moteur gcsim n'implémente pas ce personnage (trop récent).",
      "en": "Not simulatable yet — the gcsim engine does not implement this character (too recent).",
    },
    "simHowTitle": {
      "fr": "Comment ce DPS est-il calculé ?",
      "en": "How is this DPS computed?",
    },
    "simHowBody": {
      "fr":
          "La simulation utilise gcsim, le moteur open source de référence de la communauté theorycrafting : il reproduit les FORMULES DU JEU image par image (dégâts, réactions, ICD, énergie, buffs).\n\nCe qui vient de TOI (fichier GOOD) : niveaux, ascensions, constellations, talents, arme + raffinement + niveau, sets d'artefacts et toutes leurs stats.\n\nHypothèses affichées : cible niveau 100 (10 % de résistances), 90 s de combat, 100 itérations (le min/max montre la variance des crits), rotation standard simplifiée — pas un plafond théorique parfait.\n\nLimite connue : la valeur des main stats d'artefacts non montés au max est approximée linéairement. Les rotations s'affinent patch après patch via la synchro.",
      "en":
          "The simulation uses gcsim, the community's reference open-source engine: it reproduces the GAME'S FORMULAS frame by frame (damage, reactions, ICD, energy, buffs).\n\nWhat comes from YOU (GOOD file): levels, ascensions, constellations, talents, weapon + refinement + level, artifact sets and all their stats.\n\nStated assumptions: level 100 target (10% res), 90 s fight, 100 iterations (min/max shows crit variance), simplified standard rotation — not a perfect theoretical ceiling.\n\nKnown limit: main stat values of non-maxed artifacts are linearly approximated. Rotations get refined patch after patch via sync.",
    },
    "simButton": {
      "fr": "Simuler mon vrai DPS (gcsim)",
      "en": "Simulate my real DPS (gcsim)",
    },
    "simRunning": {
      "fr": "Simulation en cours… (~10-30 s)",
      "en": "Simulating… (~10-30 s)",
    },
    "simAgain": {"fr": "Relancer", "en": "Run again"},
    "simDpsLabel": {
      "fr": "DPS simulé sur TES builds",
      "en": "DPS simulated on YOUR builds",
    },
    "simNote": {
      "fr":
          "itérations · rotation standard simplifiée · moteur gcsim · à affiner via la synchro",
      "en":
          "iterations · simplified standard rotation · gcsim engine · refined via sync",
    },
    "teamsReady": {"fr": "PRÊTE", "en": "READY"},
    "teamsReadyOf": {"fr": "sur", "en": "of"},
    "teamsPlayableNow": {
      "fr": "jouables tout de suite",
      "en": "playable right now",
    },
    "teamsAllModes": {"fr": "Tous les modes", "en": "All modes"},
    "teamsNoArtifacts": {
      "fr": "aucun artefact équipé",
      "en": "no artifacts equipped",
    },
    "teamsWeakWeapon": {
      "fr": "arme non montée",
      "en": "weapon not leveled",
    },
    "dashSeeAll": {"fr": "Voir toutes les équipes", "en": "See all teams"},
    "dashNoTeamForMode": {
      "fr": "Aucune équipe curée pour ce mode pour l'instant — la BDD s'étoffe via la synchro.",
      "en": "No curated team for this mode yet — the DB grows via sync.",
    },
    "dashDpsIfComplete": {
      "fr": "DPS si complète",
      "en": "DPS if complete",
    },
    "dashSimulated": {
      "fr": "simulé sur ta box le",
      "en": "simulated on your box on",
    },
    "dashDemoTag": {
      "fr": "repère box standard — simule pour TA box",
      "en": "standard-box benchmark — simulate for YOUR box",
    },
    "contentCurrent": {"fr": "Contenu actuel", "en": "Current content"},
    "contentOngoing": {"fr": "En cours", "en": "Ongoing"},
    "contentUpcoming": {"fr": "À venir", "en": "Upcoming"},
    "contentEnded": {
      "fr": "Cycle terminé — le suivant arrivera par la synchro",
      "en": "Cycle over — the next one will arrive via sync",
    },
    "contentEndsIn": {"fr": "fin dans", "en": "ends in"},
    "contentDays": {"fr": "j", "en": "d"},
    "seasonHidden": {
      "fr": "équipe(s) masquée(s) : leurs éléments sont interdits par la saison en cours",
      "en": "team(s) hidden: their elements are banned by the current season",
    },
    "seasonAllHidden": {
      "fr": "Aucune équipe curée n'est jouable avec les éléments imposés :",
      "en": "No curated team is playable with the enforced elements:",
    },
    "contentUpdated": {"fr": "màj", "en": "updated"},
    "contentBestForYou": {
      "fr": "Meilleure option de ta box :",
      "en": "Best option from your box:",
    },
    "teamsMyCreated": {
      "fr": "Mes équipes créées",
      "en": "My created teams",
    },
    "creatorOpenIn": {
      "fr": "Ouvrir le créateur",
      "en": "Open the creator",
    },
    "creatorModeLabel": {"fr": "Mode visé :", "en": "Target mode:"},
    "dashReadyClean": {
      "fr": "Jouable tout de suite, rien à corriger",
      "en": "Playable right now, nothing to fix",
    },
    "dashIssues": {"fr": "point(s) à corriger", "en": "thing(s) to fix"},
    "dashCompleteToBuild": {
      "fr": "Complète, mais un perso est à monter",
      "en": "Complete, but a character needs building",
    },
    "teamsSuggestFor": {"fr": "en attendant :", "en": "meanwhile:"},
    "teamsNoSuggest": {
      "fr": "aucun remplaçant valable dans ta box",
      "en": "no valid replacement in your box",
    },
    "teamsToBuild": {"fr": "à monter", "en": "needs building"},
    "teamsReplaces": {"fr": "à la place de", "en": "in place of"},
    "optimizedTitle": {
      "fr": "Construites pour ce contenu, depuis ta box",
      "en": "Built for this content, from your box",
    },
    "optimizedSubtitle": {
      "fr": "Le moteur combine TES persos et applique les règles du cycle. Chaque facteur du calcul est affiché : si tu n'es pas d'accord, tu vois exactement pourquoi.",
      "en": "The engine combines YOUR characters and applies this cycle's rules. Every factor is shown: if you disagree, you can see exactly why.",
    },
    "optimizedPlayable": {
      "fr": "jouable maintenant",
      "en": "playable right now",
    },
    "optimizedMissing": {"fr": "il te manque :", "en": "you're missing:"},
    "optimizedToBuild": {"fr": "à monter :", "en": "to build:"},
    "teamsDemoNote": {
      "fr":
          "16 équipes curées, chaque rotation validée par simulation (16/16). Le croisement avec ta box, les substitutions et les DPS simulés sont réels ; la méta et les contenus de cycle se mettent à jour sans réinstaller l'app.",
      "en":
          "16 curated teams, every rotation validated by simulation (16/16). Box matching, substitutions and simulated DPS are real; meta and cycle content update without reinstalling the app.",
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
