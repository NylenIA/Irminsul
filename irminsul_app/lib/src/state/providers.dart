import "package:flutter/widgets.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

/// Langue courante (FR par défaut).
final localeProvider = StateProvider<Locale>((ref) => const Locale("fr"));

/// Résumé minimal du compte importé (Étape 1).
class AccountSummary {
  final String source; // "GOOD" ou "Enka"
  final String label; // nom du fichier ou UID
  final int characterCount;

  const AccountSummary({
    required this.source,
    required this.label,
    required this.characterCount,
  });
}

/// null = aucun compte importé.
final accountProvider = StateProvider<AccountSummary?>((ref) => null);
