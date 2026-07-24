import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/glass_card.dart";

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final account = ref.watch(accountProvider);

    return Scaffold(
      body: Container(
        decoration: appBackground(),
        child: Row(
          children: [
            _Sidebar(l: l),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(30),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l.t("greeting"),
                      style: const TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      l.t("dashboardSubtitle"),
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.6),
                      ),
                    ),
                    const SizedBox(height: 24),
                    GlassCard(
                      child: Row(
                        children: [
                          Container(
                            width: 46,
                            height: 46,
                            decoration: BoxDecoration(
                              color: kPurple.withValues(alpha: 0.18),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.check_circle,
                                color: kPurple),
                          ),
                          const SizedBox(width: 16),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                l.t("accountImported"),
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                account == null
                                    ? "—"
                                    : "${account.source} · ${account.characterCount} ${l.t("charactersCount")} · ${account.label}",
                                style: TextStyle(
                                  color: Colors.white.withValues(alpha: 0.6),
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 18),
                    GlassCard(
                      child: Row(
                        children: [
                          const Icon(Icons.auto_awesome, color: kPink),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Text(
                              l.t("comingSoon"),
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.75),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Spacer(),
                    TextButton.icon(
                      onPressed: () => context.go("/"),
                      icon: const Icon(Icons.swap_horiz, size: 18),
                      label: Text(l.t("changeAccount")),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Sidebar extends StatelessWidget {
  final L l;
  const _Sidebar({required this.l});

  @override
  Widget build(BuildContext context) {
    Widget item(IconData icon, String label, {bool active = false}) {
      return Container(
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
            Icon(icon,
                size: 20,
                color: active ? kPurple : Colors.white.withValues(alpha: 0.7)),
            const SizedBox(width: 12),
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: active ? Colors.white : Colors.white.withValues(alpha: 0.7),
                fontWeight: active ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      );
    }

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
            padding: const EdgeInsets.only(left: 6, top: 6, bottom: 22),
            child: Row(
              children: [
                Container(
                  width: 34,
                  height: 34,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(colors: [kPurple, kPink]),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Center(
                    child: Text("🌳", style: TextStyle(fontSize: 17)),
                  ),
                ),
                const SizedBox(width: 11),
                const Text(
                  "Irminsul",
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          item(Icons.dashboard, l.t("navDashboard"), active: true),
          item(Icons.people_alt, l.t("navCharacters")),
          item(Icons.shield_moon, l.t("navTeams")),
          item(Icons.compare_arrows, l.t("navCompare")),
          item(Icons.menu_book, l.t("navGuides")),
          item(Icons.track_changes, l.t("navFarm")),
          const Spacer(),
          item(Icons.settings, l.t("navSettings")),
        ],
      ),
    );
  }
}
