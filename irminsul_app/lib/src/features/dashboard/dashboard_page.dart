import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/meta_repository.dart";
import "../../i18n/strings.dart";
import "../../services/patch_service.dart";
import "../../state/providers.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/hover_card.dart";
import "../../widgets/reveal.dart";

/// Mode sélectionné (abyss | theater | onslaught).
final _modeProvider = StateProvider<String>((ref) => "abyss");

/// Tableau de bord v2 — façon maquette : teams par mode, DPS animé,
/// « ce qui te manque ». Données de DÉMO en attendant la BDD méta + gcsim.
class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final account = ref.watch(accountProvider);
    final mode = ref.watch(_modeProvider);
    final metaDb = ref.watch(metaDbProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ---- entête ----
          Reveal(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        account?.playerName == null
                            ? l.t("greeting")
                            : "${l.t("greetingName")} ${account!.playerName}",
                        style: const TextStyle(
                            fontSize: 26, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        metaDb.maybeWhen(
                          data: (db) =>
                              "${l.t("bestTeamsFor")} — patch ${db.metaVersion}",
                          orElse: () => l.t("dashboardSubtitle"),
                        ),
                        style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.6)),
                      ),
                    ],
                  ),
                ),
                _SyncChip(l: l),
                const SizedBox(width: 10),
                if (account != null)
                  _AccountChip(
                    text:
                        "${account.source} · ${account.characterCount} ${l.t("charactersCount")}",
                  ),
              ],
            ),
          ),
          const SizedBox(height: 22),

          // ---- onglets de mode ----
          Reveal(
            delayMs: 80,
            child: Row(
              children: [
                _ModeTab(label: l.t("modeAbyss"), id: "abyss", current: mode),
                _ModeTab(
                    label: l.t("modeTheater"), id: "theater", current: mode),
                _ModeTab(
                    label: l.t("modeOnslaught"),
                    id: "onslaught",
                    current: mode),
              ],
            ),
          ),
          const SizedBox(height: 18),

          // ---- teams du mode ----
          metaDb.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(40),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (e, _) => GlassCard(child: Text("Erreur données méta : $e")),
            data: (db) {
              final teams = db.byMode(mode);
              return AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                switchInCurve: Curves.easeOutCubic,
                child: Column(
                  key: ValueKey(mode),
                  children: [
                    for (var i = 0; i < teams.length; i++) ...[
                      Reveal(
                        delayMs: 120 + i * 90,
                        child: _TeamCard(team: teams[i], l: l),
                      ),
                      const SizedBox(height: 16),
                    ],
                    Reveal(
                      delayMs: 120 + teams.length * 90,
                      child: Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Row(
                          children: [
                            Icon(Icons.science_outlined,
                                size: 14,
                                color: Colors.white.withValues(alpha: 0.35)),
                            const SizedBox(width: 6),
                            Text(
                              l.t("demoDataNote"),
                              style: TextStyle(
                                fontSize: 11.5,
                                color: Colors.white.withValues(alpha: 0.35),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),

          const SizedBox(height: 10),
          Reveal(
            delayMs: 500,
            child: TextButton.icon(
              onPressed: () => context.go("/"),
              icon: const Icon(Icons.swap_horiz, size: 18),
              label: Text(l.t("changeAccount")),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------- widgets --

class _AccountChip extends StatelessWidget {
  final String text;
  const _AccountChip({required this.text});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.045),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.09)),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle, size: 15, color: cs.primary),
          const SizedBox(width: 8),
          Text(text, style: const TextStyle(fontSize: 12.5)),
        ],
      ),
    );
  }
}

class _ModeTab extends ConsumerWidget {
  final String label;
  final String id;
  final String current;
  const _ModeTab(
      {required this.label, required this.id, required this.current});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cs = Theme.of(context).colorScheme;
    final active = id == current;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        borderRadius: BorderRadius.circular(11),
        onTap: () => ref.read(_modeProvider.notifier).state = id,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOutCubic,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 9),
          decoration: BoxDecoration(
            gradient: active
                ? LinearGradient(colors: [cs.primary, cs.secondary])
                : null,
            color: active ? null : Colors.white.withValues(alpha: 0.045),
            borderRadius: BorderRadius.circular(11),
            border: active
                ? null
                : Border.all(color: Colors.white.withValues(alpha: 0.09)),
            boxShadow: active
                ? [
                    BoxShadow(
                      color: cs.secondary.withValues(alpha: 0.28),
                      blurRadius: 22,
                      offset: const Offset(0, 8),
                    ),
                  ]
                : const [],
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 13.5,
              color: active ? Colors.white : Colors.white70,
              fontWeight: active ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }
}

class _TeamCard extends StatelessWidget {
  final MetaTeam team;
  final L l;
  const _TeamCard({required this.team, required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final locked = team.badge == "locked";

    return HoverCard(
      glow: locked ? Colors.white24 : cs.primary,
      child: GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        team.half.toUpperCase(),
                        style: TextStyle(
                          fontSize: 11,
                          letterSpacing: 1.3,
                          color: Colors.white.withValues(alpha: 0.45),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        team.name,
                        style: const TextStyle(
                            fontSize: 17, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                _Badge(kind: team.badge, l: l),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                for (final c in team.chars)
                  Padding(
                    padding: const EdgeInsets.only(right: 14),
                    child: CharIcon(
                      name: c.name,
                      icon: c.icon,
                      element: c.element,
                      dimmed: locked,
                    ),
                  ),
                const Spacer(),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    CountUp(
                      value: team.dps,
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w800,
                        color: locked
                            ? Colors.white.withValues(alpha: 0.4)
                            : cs.primary,
                      ),
                    ),
                    Text(
                      l.t("dpsPerRotation"),
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.white.withValues(alpha: 0.45),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _Meta(text: "${l.t("rotationLabel")} ${team.rotation}"),
                const SizedBox(width: 16),
                _Meta(text: team.note),
              ],
            ),
            if (team.missing != null) ...[
              const SizedBox(height: 14),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(13),
                decoration: BoxDecoration(
                  color: cs.secondary.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(13),
                  border: Border.all(
                      color: cs.secondary.withValues(alpha: 0.28)),
                ),
                child: Text(
                  "${l.t("missingPrefix")} ${team.missing!.character} — ${team.missing!.gain} ${l.t("missingSuffix")}",
                  style: const TextStyle(fontSize: 13),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String kind;
  final L l;
  const _Badge({required this.kind, required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    late final String text;
    late final Widget badge;
    switch (kind) {
      case "meta":
        text = l.t("badgeMeta");
        badge = Container(
          padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 5),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [cs.primary, cs.secondary]),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(text,
              style: const TextStyle(
                  fontSize: 10.5,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8)),
        );
      case "locked":
        text = l.t("badgeLocked");
        badge = Container(
          padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 5),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
          ),
          child: Text("🔒 $text",
              style: TextStyle(
                  fontSize: 10.5,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: Colors.white.withValues(alpha: 0.6))),
        );
      default:
        text = l.t("badgeViable");
        badge = Container(
          padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 5),
          decoration: BoxDecoration(
            color: cs.tertiary.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: cs.tertiary.withValues(alpha: 0.3)),
          ),
          child: Text(text,
              style: TextStyle(
                  fontSize: 10.5,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: cs.tertiary)),
        );
    }
    return badge;
  }
}

class _SyncChip extends ConsumerWidget {
  final L l;
  const _SyncChip({required this.l});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sync = ref.watch(syncStatusProvider);
    return sync.maybeWhen(
      data: (s) {
        final (color, text) = switch (s.state) {
          SyncState.upToDate => (
              const Color(0xFF8BE28B),
              "${l.t("syncUpToDate")} · ${s.localVersion}"
            ),
          SyncState.updateAvailable => (
              const Color(0xFFF2C14E),
              "${l.t("syncUpdate")} ${s.remoteVersion}"
            ),
          SyncState.offline => (
              Colors.white38,
              "${l.t("syncOffline")} · ${s.localVersion}"
            ),
        };
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.045),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white.withValues(alpha: 0.09)),
          ),
          child: Row(
            children: [
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                        color: color.withValues(alpha: 0.6), blurRadius: 7),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Text(text, style: const TextStyle(fontSize: 12)),
            ],
          ),
        );
      },
      orElse: () => const SizedBox.shrink(),
    );
  }
}

class _Meta extends StatelessWidget {
  final String text;
  const _Meta({required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 4,
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.35),
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 7),
        Text(
          text,
          style: TextStyle(
            fontSize: 12,
            color: Colors.white.withValues(alpha: 0.55),
          ),
        ),
      ],
    );
  }
}
