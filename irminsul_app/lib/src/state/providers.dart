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

/// La box complète du joueur (GOOD sauvegardé sur disque, rechargé au
/// démarrage). null = pas encore importée. Invalider après un import.
final boxProvider =
    FutureProvider<PlayerBox?>((ref) => BoxService.loadSaved());
