import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../../i18n/strings.dart";
import "../../services/engine_info_service.dart";
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

          // --- Moteur de simulation (fraîcheur vérifiée en direct) ---
          const _EngineCard(),
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

/// Carte « moteur de simulation » : version embarquée, fraîcheur vérifiée
/// en direct contre les releases officielles de gcsim.
class _EngineCard extends ConsumerWidget {
  const _EngineCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final status = ref.watch(engineStatusProvider);

    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l.t("settingsEngine"),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          Text(
            l.t("settingsEngineDesc"),
            style: TextStyle(
              fontSize: 13,
              height: 1.45,
              color: Colors.white.withValues(alpha: 0.6),
            ),
          ),
          const SizedBox(height: 14),
          status.when(
            loading: () => const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            error: (e, _) => Text("—",
                style: TextStyle(color: Colors.white.withValues(alpha: 0.5))),
            data: (s) {
              final (color, label) = switch (s.state) {
                EngineFreshness.upToDate => (
                    const Color(0xFF8BE28B),
                    l.t("engineUpToDate")
                  ),
                EngineFreshness.outdated => (
                    const Color(0xFFF2C14E),
                    l.t("engineOutdated")
                  ),
                EngineFreshness.localDev => (
                    Colors.white38,
                    l.t("engineLocalDev")
                  ),
                EngineFreshness.offline => (
                    Colors.white38,
                    l.t("engineOffline")
                  ),
              };
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                                color: color.withValues(alpha: 0.6),
                                blurRadius: 8),
                          ],
                        ),
                      ),
                      const SizedBox(width: 9),
                      Text(
                        label,
                        style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: color),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  _kv(l.t("engineBuild"),
                      "gcsim ${s.info.shortCommit} · ${_fmtDate(s.info.builtAt)}"),
                  if (s.liveRelease != null)
                    _kv(l.t("engineLatestRelease"),
                        "${s.liveRelease} (${_fmtDate(s.livePublished!)})"),
                  if (s.info.extraPRs.isNotEmpty)
                    _kv(l.t("engineExtras"), s.info.extraPRs.join(" · ")),
                  const SizedBox(height: 8),
                  Text(
                    l.t("engineDaily"),
                    style: TextStyle(
                      fontSize: 11.5,
                      height: 1.4,
                      color: Colors.white.withValues(alpha: 0.45),
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  static String _fmtDate(DateTime d) =>
      "${d.day.toString().padLeft(2, "0")}/${d.month.toString().padLeft(2, "0")}/${d.year}";

  static Widget _kv(String k, String v) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 140,
              child: Text(k,
                  style: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w600)),
            ),
            Expanded(
              child: Text(v,
                  style: TextStyle(
                      fontSize: 12,
                      color: Colors.white.withValues(alpha: 0.6))),
            ),
          ],
        ),
      );
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
