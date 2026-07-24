import "package:flutter/widgets.dart";

/// i18n minimaliste et robuste (FR/EN) — architecture prête à s'étendre.
/// Pas de génération de code : un simple dictionnaire, sélectionné par la locale.
class L {
  final Locale locale;
  const L(this.locale);

  static const supported = [Locale("fr"), Locale("en")];

  String get code => locale.languageCode;

  String t(String key) =>
      _data[key]?[code] ?? _data[key]?["en"] ?? key;

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
      "en": "Choose your .json in GOOD format (Inventory Kamera / Genshin Optimizer).",
    },
    "importGoodButton": {"fr": "Choisir un fichier", "en": "Choose a file"},
    "importEnkaTitle": {"fr": "Ou utilise ton UID", "en": "Or use your UID"},
    "importEnkaDesc": {
      "fr": "Récupère ta vitrine via Enka.network (bientôt).",
      "en": "Fetch your showcase via Enka.network (coming soon).",
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
    "navDashboard": {"fr": "Tableau de bord", "en": "Dashboard"},
    "navCharacters": {"fr": "Mes personnages", "en": "My characters"},
    "navTeams": {"fr": "Équipes", "en": "Teams"},
    "navCompare": {"fr": "Comparateur", "en": "Compare"},
    "navGuides": {"fr": "Guides persos", "en": "Character guides"},
    "navFarm": {"fr": "Que farmer", "en": "What to farm"},
    "navSettings": {"fr": "Réglages", "en": "Settings"},
  };
}
