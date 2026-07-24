import "package:flutter/widgets.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:shared_preferences/shared_preferences.dart";

/// Langue courante (FR par défaut ; surchargée au démarrage si sauvegardée).
final localeProvider = StateProvider<Locale>((ref) => const Locale("fr"));

/// Identifiant de la palette d'accent (voir accentPalettes).
final accentProvider = StateProvider<String>((ref) => "irminsul");

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

  const AccountSummary({
    required this.source,
    required this.label,
    required this.characterCount,
  });
}

/// null = aucun compte importé.
final accountProvider = StateProvider<AccountSummary?>((ref) => null);
