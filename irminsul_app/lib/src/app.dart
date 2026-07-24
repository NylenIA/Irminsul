import "package:flutter/material.dart";
import "package:flutter_localizations/flutter_localizations.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "i18n/strings.dart";
import "router.dart";
import "state/providers.dart";
import "theme.dart";

/// Racine de l'application Irminsul.
class IrminsulApp extends ConsumerWidget {
  const IrminsulApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    final palette = paletteOf(ref.watch(accentProvider));
    return MaterialApp.router(
      title: "Irminsul",
      debugShowCheckedModeBanner: false,
      theme: buildTheme(palette),
      locale: locale,
      supportedLocales: L.supported,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      routerConfig: appRouter,
    );
  }
}
