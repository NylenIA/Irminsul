import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter/widgets.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:shared_preferences/shared_preferences.dart";

import "../services/box_service.dart";

/// Langue courante (FR par défaut ; surchargée au démarrage si sauvegardée).
final localeProvider = StateProvider<Locale>((ref) => const Locale("fr"));

/// Identifiant de la palette d'accent (voir accentPalettes).
final accentProvider = StateProvider<String>((ref) => "irminsul");

/// Voyageur choisi : "aether" ou "lumine" (affiché dans la Gazette).
final travelerProvider = StateProvider<String>((ref) => "aether");

/// Sauvegarde d'un réglage (clé "lang" / "accent").
Future<void> persistSetting(String key, String value) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(key, value);
}

/// Résumé minimal du compte importé.
class AccountSummary {
  final String source; // "GOOD" ou "Enka"
  final String label;
  final int characterCount;
  final String? playerName;

  const AccountSummary({
    required this.source,
    required this.label,
    required this.characterCount,
    this.playerName,
  });
}

/// null = aucun compte importé.
final accountProvider = StateProvider<AccountSummary?>((ref) => null);

/// Table ER% exacte par arme et par niveau (générée depuis les données du jeu).
final erWeaponsProvider =
    FutureProvider<Map<String, List<double>>>((ref) async {
  final raw = await rootBundle.loadString("assets/data/weapons_er.json");
  final json = jsonDecode(raw) as Map<String, dynamic>;
  return json.map((k, v) =>
      MapEntry(k, (v as List).map((x) => (x as num).toDouble()).toList()));
});

/// La box complète du joueur (GOOD sauvegardé sur disque, rechargé au
/// démarrage). null = pas encore importée. Invalider après un import.
final boxProvider = FutureProvider<PlayerBox?>((ref) async {
  final erWeapons = await ref.watch(erWeaponsProvider.future);
  return BoxService.loadSaved(erWeapons: erWeapons);
});
