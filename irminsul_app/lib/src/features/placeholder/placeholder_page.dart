import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";

/// Page « en construction » stylée pour les onglets à venir.
class PlaceholderPage extends ConsumerWidget {
  final String tab;
  const PlaceholderPage({super.key, required this.tab});

  static const _meta = {
    "characters": (Icons.people_alt, "navCharacters"),
    "teams": (Icons.shield_moon, "navTeams"),
    "compare": (Icons.compare_arrows, "navCompare"),
    "guides": (Icons.menu_book, "navGuides"),
    "farm": (Icons.track_changes, "navFarm"),
    "settings": (Icons.settings, "navSettings"),
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final entry = _meta[tab] ?? (Icons.auto_awesome, "navDashboard");

    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 84,
            height: 84,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [
                  kPurple.withValues(alpha: 0.25),
                  kCyan.withValues(alpha: 0.18),
                ],
              ),
            ),
            child: Icon(entry.$1, size: 38, color: Colors.white),
          ),
          const SizedBox(height: 22),
          Text(
            l.t(entry.$2),
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            l.t("underConstruction"),
            style: TextStyle(color: Colors.white.withValues(alpha: 0.55)),
          ),
        ],
      ),
    );
  }
}
