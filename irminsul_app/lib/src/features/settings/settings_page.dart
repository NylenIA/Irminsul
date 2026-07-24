import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";

/// Réglages : couleur du thème (palettes) + langue.
class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final currentAccent = ref.watch(accentProvider);
    final currentLang = ref.watch(localeProvider).languageCode;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l.t("navSettings"),
            style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),

          // --- Thème ---
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l.t("settingsTheme"),
                  style: const TextStyle(
                      fontSize: 17, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Text(
                  l.t("settingsThemeDesc"),
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withValues(alpha: 0.6),
                  ),
                ),
                const SizedBox(height: 18),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    for (final p in accentPalettes.values)
                      _PaletteTile(
                        palette: p,
                        active: p.id == currentAccent,
                        onTap: () {
                          ref.read(accentProvider.notifier).state = p.id;
                          persistSetting("accent", p.id);
                        },
                      ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),

          // --- Voyageur / Voyageuse ---
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l.t("settingsTraveler"),
                  style: const TextStyle(
                      fontSize: 17, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Text(
                  l.t("settingsTravelerDesc"),
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withValues(alpha: 0.6),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _TravelerTile(
                      id: "aether",
                      name: "Aether",
                      icon: "UI_AvatarIcon_PlayerBoy",
                      active: ref.watch(travelerProvider) == "aether",
                      onTap: () {
                        ref.read(travelerProvider.notifier).state = "aether";
                        persistSetting("traveler", "aether");
                      },
                    ),
                    const SizedBox(width: 12),
                    _TravelerTile(
                      id: "lumine",
                      name: "Lumine",
                      icon: "UI_AvatarIcon_PlayerGirl",
                      active: ref.watch(travelerProvider) == "lumine",
                      onTap: () {
                        ref.read(travelerProvider.notifier).state = "lumine";
                        persistSetting("traveler", "lumine");
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),

          // --- Langue ---
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l.t("settingsLanguage"),
                  style: const TextStyle(
                      fontSize: 17, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    for (final code in ["fr", "en"])
                      Padding(
                        padding: const EdgeInsets.only(right: 10),
                        child: ChoiceChip(
                          label: Text(code == "fr" ? "Français" : "English"),
                          selected: currentLang == code,
                          onSelected: (_) {
                            ref.read(localeProvider.notifier).state =
                                Locale(code);
                            persistSetting("lang", code);
                          },
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TravelerTile extends StatelessWidget {
  final String id;
  final String name;
  final String icon;
  final bool active;
  final VoidCallback onTap;
  const _TravelerTile({
    required this.id,
    required this.name,
    required this.icon,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 150,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: active ? 0.09 : 0.04),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color:
                active ? cs.primary : Colors.white.withValues(alpha: 0.09),
            width: active ? 1.6 : 1,
          ),
        ),
        child: Row(
          children: [
            CharIcon(
              name: name,
              icon: icon,
              element: "none",
              size: 42,
              showName: false,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                name,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: active ? FontWeight.bold : FontWeight.w500,
                ),
              ),
            ),
            if (active) Icon(Icons.check_circle, size: 18, color: cs.primary),
          ],
        ),
      ),
    );
  }
}

class _PaletteTile extends StatelessWidget {
  final AccentPalette palette;
  final bool active;
  final VoidCallback onTap;
  const _PaletteTile({
    required this.palette,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 148,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: active ? 0.09 : 0.04),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: active
                ? palette.primary
                : Colors.white.withValues(alpha: 0.09),
            width: active ? 1.6 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                _dot(palette.primary),
                _dot(palette.secondary),
                _dot(palette.tertiary),
                const Spacer(),
                if (active)
                  Icon(Icons.check_circle,
                      size: 18, color: palette.primary),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              palette.name,
              style: TextStyle(
                fontSize: 13.5,
                fontWeight: active ? FontWeight.bold : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _dot(Color c) => Container(
        width: 18,
        height: 18,
        margin: const EdgeInsets.only(right: 6),
        decoration: BoxDecoration(
          color: c,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(color: c.withValues(alpha: 0.5), blurRadius: 8),
          ],
        ),
      );
}
