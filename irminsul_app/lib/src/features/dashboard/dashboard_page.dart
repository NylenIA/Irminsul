import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../data/meta_repository.dart";
import "../../data/team_matcher.dart";
import "../../i18n/strings.dart";
import "../../services/patch_service.dart";
import "../../state/providers.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/hover_card.dart";
import "../../widgets/reveal.dart";

const _green = Color(0xFF8BE28B);
const _amber = Color(0xFFF2C14E);
const _cyan = Color(0xFF22D3EE);

/// Mode sélectionné (abyss | theater | onslaught).
final _modeProvider = StateProvider<String>((ref) => "abyss");

/// Tableau de bord : TES meilleures équipes pour le mode choisi, classées
/// par jouabilité réelle (croisement avec ta box).
class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final account = ref.watch(accountProvider);
    final mode = ref.watch(_modeProvider);
    final metaDb = ref.watch(metaDbProvider);
    final box = ref.watch(boxProvider);
    final chars = ref.watch(charactersFullProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ---- entête ----
          Reveal(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
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
            delayMs: 60,
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

          // ---- équipes croisées avec la box ----
          box.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(30),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (e, _) => GlassCard(child: Text("Erreur box : $e")),
            data: (playerBox) {
              if (playerBox == null) return Reveal(child: _ImportCta(l: l));
              return metaDb.when(
                loading: () => const Padding(
                  padding: EdgeInsets.all(30),
                  child: Center(child: CircularProgressIndicator()),
                ),
                error: (e, _) => GlassCard(child: Text("Erreur méta : $e")),
                data: (db) => chars.when(
                  loading: () => const Padding(
                    padding: EdgeInsets.all(30),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                  error: (e, _) => GlassCard(child: Text("Erreur : $e")),
                  data: (list) {
                    final matches =
                        matchTeams(meta: db, box: playerBox, characters: list)
                            .where((m) => m.team.mode == mode)
                            .toList();
                    if (matches.isEmpty) {
                      return GlassCard(
                        child: Text(l.t("dashNoTeamForMode")),
                      );
                    }
                    final top = matches.take(3).toList();
                    return AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      switchInCurve: Curves.easeOutCubic,
                      child: Column(
                        key: ValueKey(mode),
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          for (var i = 0; i < top.length; i++) ...[
                            Reveal(
                              delayMs: 80 + i * 90,
                              child: _TeamRow(match: top[i], l: l, rank: i + 1),
                            ),
                            const SizedBox(height: 14),
                          ],
                          Reveal(
                            delayMs: 100 + top.length * 90,
                            child: Row(
                              children: [
                                TextButton.icon(
                                  onPressed: () => context.go("/teams"),
                                  icon: const Icon(Icons.list_alt, size: 17),
                                  label: Text(
                                      "${l.t("dashSeeAll")} (${matches.length})"),
                                ),
                                const Spacer(),
                                TextButton.icon(
                                  onPressed: () => context.go("/"),
                                  icon: const Icon(Icons.swap_horiz, size: 17),
                                  label: Text(l.t("changeAccount")),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 6),
                          Reveal(
                            delayMs: 140 + top.length * 90,
                            child: Row(
                              children: [
                                Icon(Icons.science_outlined,
                                    size: 14,
                                    color: Colors.white
                                        .withValues(alpha: 0.35)),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    l.t("demoDataNote"),
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      color: Colors.white
                                          .withValues(alpha: 0.35),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------- widgets --

class _ImportCta extends StatelessWidget {
  final L l;
  const _ImportCta({required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GlassCard(
      padding: const EdgeInsets.all(26),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.auto_awesome, color: cs.secondary, size: 28),
          const SizedBox(height: 14),
          Text(
            l.t("teamsNoBox"),
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            l.t("teamsNoBoxDesc"),
            style: TextStyle(
              fontSize: 13,
              height: 1.5,
              color: Colors.white.withValues(alpha: 0.6),
            ),
          ),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: () => context.go("/"),
            icon: const Icon(Icons.upload_file, size: 18),
            label: Text(l.t("teamsNoBoxCta")),
          ),
        ],
      ),
    );
  }
}

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
              _green,
              "${l.t("syncUpToDate")} · ${s.localVersion}"
            ),
          SyncState.updateAvailable => (
              _amber,
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

/// Ligne compacte : rang, persos (état réel), verdict, DPS honnête.
class _TeamRow extends StatelessWidget {
  final TeamMatch match;
  final L l;
  final int rank;
  const _TeamRow({required this.match, required this.l, required this.rank});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final t = match.team;
    final color = match.ready
        ? _green
        : match.complete
            ? _cyan
            : _amber;

    return HoverCard(
      glow: color,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => context.go("/teams"),
        child: GlassCard(
          child: Row(
            children: [
              // rang
              Container(
                width: 30,
                height: 30,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(
                  child: Text(
                    "$rank",
                    style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: color),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              // persos
              for (final s in match.slots)
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: CharIcon(
                    name: s.character.name,
                    icon: s.character.icon,
                    element: s.character.element,
                    size: 42,
                    dimmed: !s.owned,
                    showName: false,
                  ),
                ),
              const SizedBox(width: 10),
              // nom + verdict
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      t.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 15, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      _verdict(l),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 11.5,
                        color: color.withValues(alpha: 0.95),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              // DPS : honnête (indicatif, et « si complète » si des slots manquent)
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    _fmt(t.dps),
                    style: TextStyle(
                      fontSize: 19,
                      fontWeight: FontWeight.w800,
                      color: match.complete
                          ? cs.primary
                          : Colors.white.withValues(alpha: 0.35),
                    ),
                  ),
                  Text(
                    match.complete
                        ? l.t("dpsPerRotation")
                        : l.t("dashDpsIfComplete"),
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.white.withValues(alpha: 0.4),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _verdict(L l) {
    if (match.ready) {
      final issues = match.issueCount;
      return issues == 0
          ? l.t("dashReadyClean")
          : "${l.t("teamsReady")} · $issues ${l.t("dashIssues")}";
    }
    if (match.complete) return l.t("dashCompleteToBuild");
    final first = match.missing.first;
    final sug = first.suggestion;
    return sug == null
        ? "${l.t("teamsMissingPrefix")} ${first.character.name}"
        : "${l.t("teamsMissingPrefix")} ${first.character.name} → ${sug.name}";
  }

  static String _fmt(int v) {
    final s = v.toString();
    final b = StringBuffer();
    for (var i = 0; i < s.length; i++) {
      if (i > 0 && (s.length - i) % 3 == 0) b.write(" ");
      b.write(s[i]);
    }
    return b.toString();
  }
}
