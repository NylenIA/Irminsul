import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:shared_preferences/shared_preferences.dart";

import "src/app.dart";
import "src/state/providers.dart";

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final accent = prefs.getString("accent") ?? "irminsul";
  final lang = prefs.getString("lang") ?? "fr";
  final traveler = prefs.getString("traveler") ?? "aether";

  runApp(
    ProviderScope(
      overrides: [
        accentProvider.overrideWith((ref) => accent),
        localeProvider.overrideWith((ref) => Locale(lang)),
        travelerProvider.overrideWith((ref) => traveler),
      ],
      child: const IrminsulApp(),
    ),
  );
}
