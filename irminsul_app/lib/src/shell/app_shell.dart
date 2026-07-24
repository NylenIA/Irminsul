import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../i18n/strings.dart";
import "../state/providers.dart";
import "../widgets/aurora_background.dart";
import "../widgets/irminsul_logo.dart";

/// Coquille persistante : barre latérale + contenu de l'onglet actif.
class AppShell extends ConsumerWidget {
  final Widget child;
  final String location;
  const AppShell({super.key, required this.child, required this.location});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    return Scaffold(
      body: AuroraBackground(
        child: Row(
          children: [
            _Sidebar(l: l, location: location),
            Expanded(child: child),
          ],
        ),
      ),
    );
  }
}

class _NavItem {
  final String path;
  final IconData icon;
  final String labelKey;
  const _NavItem(this.path, this.icon, this.labelKey);
}

const _mainNav = [
  _NavItem("/dashboard", Icons.dashboard, "navDashboard"),
  _NavItem("/characters", Icons.people_alt, "navCharacters"),
  _NavItem("/teams", Icons.shield_moon, "navTeams"),
  _NavItem("/compare", Icons.compare_arrows, "navCompare"),
];

const _resNav = [
  _NavItem("/guides", Icons.menu_book, "navGuides"),
  _NavItem("/farm", Icons.track_changes, "navFarm"),
];

class _Sidebar extends StatelessWidget {
  final L l;
  final String location;
  const _Sidebar({required this.l, required this.location});

  Widget _label(String text) => Padding(
        padding: const EdgeInsets.only(left: 10, top: 16, bottom: 6),
        child: Text(
          text.toUpperCase(),
          style: TextStyle(
            fontSize: 11,
            letterSpacing: 1.4,
            color: Colors.white.withValues(alpha: 0.4),
          ),
        ),
      );

  Widget _item(BuildContext context, _NavItem item) {
    final active = location == item.path;
    final accent = Theme.of(context).colorScheme.primary;
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: () => context.go(item.path),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        margin: const EdgeInsets.symmetric(vertical: 3),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
        decoration: BoxDecoration(
          color: active ? Colors.white.withValues(alpha: 0.07) : null,
          borderRadius: BorderRadius.circular(12),
          border: active
              ? Border.all(color: Colors.white.withValues(alpha: 0.09))
              : null,
        ),
        child: Row(
          children: [
            Icon(
              item.icon,
              size: 20,
              color: active ? accent : Colors.white.withValues(alpha: 0.7),
            ),
            const SizedBox(width: 12),
            Text(
              l.t(item.labelKey),
              style: TextStyle(
                fontSize: 14,
                color: active
                    ? Colors.white
                    : Colors.white.withValues(alpha: 0.7),
                fontWeight: active ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 236,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.02),
        border: Border(
          right: BorderSide(color: Colors.white.withValues(alpha: 0.09)),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 4, top: 4, bottom: 10),
            child: Row(
              children: [
                const IrminsulLogo(size: 40, animated: false),
                const SizedBox(width: 10),
                const Text(
                  "Irminsul",
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          _label(l.t("sectionMain")),
          for (final item in _mainNav) _item(context, item),
          _label(l.t("sectionResources")),
          for (final item in _resNav) _item(context, item),
          const Spacer(),
          _item(context, const _NavItem("/settings", Icons.settings, "navSettings")),
        ],
      ),
    );
  }
}
