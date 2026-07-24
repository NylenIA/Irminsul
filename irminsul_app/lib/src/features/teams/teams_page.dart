import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../data/meta_repository.dart";
import "../../data/team_matcher.dart";
import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/hover_card.dart";
import "../../widgets/reveal.dart";

const _green = Color(0xFF8BE28B);
const _amber = Color(0xFFF2C14E);
const _cyan = Color(0xFF22D3EE);

/// Filtre de mode de la page Équipes (null = tous).
final _teamsModeProvider = StateProvider<String?>((ref) => null);

/// Team Builder : la BDD méta croisée avec TA box (fichier GOOD importé).
/// Règle produit : jamais de bricolage — un slot manquant est dit manquant.
class TeamsPage extends ConsumerWidget {
  const TeamsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final box = ref.watch(boxProvider);
    final meta = ref.watch(metaDbProvider);
    final chars = ref.watch(charactersFullProvider);
    final mode = ref.watch(_teamsModeProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Reveal(
            child: Text(
              l.t("navTeams"),
              style:
                  const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 4),
          Reveal(
            delayMs: 50,
            child: Text(
              l.t("teamsSubtitle"),
              style: TextStyle(color: Colors.white.withValues(alpha: 0.6)),
            ),
          ),
          const SizedBox(height: 22),
          box.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => GlassCard(child: Text("Erreur box : $e")),
            data: (playerBox) {
              if (playerBox == null) {
                return Reveal(child: _NoBoxCard(l: l));
              }
              return meta.when(
                loading: () =>
                    const Center(child: CircularProgressIndicator()),
                error: (e, _) => GlassCard(child: Text("Erreur méta : $e")),
                data: (db) => chars.when(
                  loading: () =>
                      const Center(child: CircularProgressIndicator()),
                  error: (e, _) => GlassCard(child: Text("Erreur : $e")),
                  data: (list) {
                    final all = matchTeams(
                        meta: db, box: playerBox, characters: list);
                    final shown = mode == null
                        ? all
                        : all.where((m) => m.team.mode == mode).toList();
                    final ready = all.where((m) => m.ready).length;
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Reveal(
                          child: Wrap(
                            spacing: 10,
                            runSpacing: 10,
                            crossAxisAlignment: WrapCrossAlignment.center,
                            children: [
                              _BoxChip(
                                  count: playerBox.count,
                                  label: playerBox.label,
                                  l: l),
                              _ReadyChip(ready: ready, total: all.length, l: l),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),
                        Reveal(
                          delayMs: 40,
                          child: Row(
                            children: [
                              _ModeFilter(
                                  label: l.t("teamsAllModes"),
                                  value: null,
                                  current: mode),
                              _ModeFilter(
                                  label: l.t("modeAbyss"),
                                  value: "abyss",
                                  current: mode),
                              _ModeFilter(
                                  label: l.t("modeTheater"),
                                  value: "theater",
                                  current: mode),
                              _ModeFilter(
                                  label: l.t("modeOnslaught"),
                                  value: "onslaught",
                                  current: mode),
                            ],
                          ),
                        ),
                        const SizedBox(height: 18),
                        for (var i = 0; i < shown.length; i++) ...[
                          Reveal(
                            delayMs: 60 + (i.clamp(0, 8)) * 70,
                            child: _TeamMatchCard(match: shown[i], l: l),
                          ),
                          const SizedBox(height: 16),
                        ],
                        Reveal(
                          child: Row(
                            children: [
                              Icon(Icons.science_outlined,
                                  size: 14,
                                  color:
                                      Colors.white.withValues(alpha: 0.35)),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  l.t("teamsDemoNote"),
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

// ------------------------------------------------------------------ chips --

class _NoBoxCard extends StatelessWidget {
  final L l;
  const _NoBoxCard({required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GlassCard(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.inventory_2_outlined, color: cs.primary, size: 30),
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

class _BoxChip extends StatelessWidget {
  final int count;
  final String label;
  final L l;
  const _BoxChip({required this.count, required this.label, required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.045),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.09)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.inventory_2, size: 15, color: cs.primary),
          const SizedBox(width: 8),
          Text(
            "${l.t("teamsCrossedWith")} $count ${l.t("charactersCount")} · $label",
            style: const TextStyle(fontSize: 12.5),
          ),
        ],
      ),
    );
  }
}

class _ReadyChip extends StatelessWidget {
  final int ready;
  final int total;
  final L l;
  const _ReadyChip(
      {required this.ready, required this.total, required this.l});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: _green.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _green.withValues(alpha: 0.35)),
      ),
      child: Text(
        "✓ $ready ${l.t("teamsReadyOf")} $total ${l.t("teamsPlayableNow")}",
        style: const TextStyle(
            fontSize: 12.5, fontWeight: FontWeight.w700, color: _green),
      ),
    );
  }
}

class _ModeFilter extends ConsumerWidget {
  final String label;
  final String? value;
  final String? current;
  const _ModeFilter(
      {required this.label, required this.value, required this.current});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cs = Theme.of(context).colorScheme;
    final active = value == current;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        borderRadius: BorderRadius.circular(11),
        onTap: () => ref.read(_teamsModeProvider.notifier).state = value,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            gradient: active
                ? LinearGradient(colors: [cs.primary, cs.secondary])
                : null,
            color: active ? null : Colors.white.withValues(alpha: 0.045),
            borderRadius: BorderRadius.circular(11),
            border: active
                ? null
                : Border.all(color: Colors.white.withValues(alpha: 0.09)),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12.5,
              fontWeight: active ? FontWeight.w700 : FontWeight.normal,
              color: active ? Colors.white : Colors.white70,
            ),
          ),
        ),
      ),
    );
  }
}

// ------------------------------------------------------------------- card --

class _TeamMatchCard extends StatelessWidget {
  final TeamMatch match;
  final L l;
  const _TeamMatchCard({required this.match, required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final t = match.team;

    return HoverCard(
      glow: match.ready ? _green : (match.complete ? cs.primary : Colors.white24),
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
                        "${_modeLabel(t.mode, l)} · ${t.half}".toUpperCase(),
                        style: TextStyle(
                          fontSize: 10.5,
                          letterSpacing: 1.2,
                          color: Colors.white.withValues(alpha: 0.45),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        t.name,
                        style: const TextStyle(
                            fontSize: 17, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                _StatusBadge(match: match, l: l),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 16,
              runSpacing: 12,
              children: [
                for (final s in match.slots) _SlotView(s: s, l: l),
              ],
            ),

            // ---- slots manquants + remplaçant possédé ----
            if (match.missing.isNotEmpty) ...[
              const SizedBox(height: 12),
              _InfoBlock(
                color: Colors.white24,
                lines: [
                  for (final s in match.missing)
                    s.suggestion != null
                        ? "🔒 ${s.character.name} — ${l.t("teamsSuggestFor")} "
                            "${s.suggestion!.name} (C${s.suggestionData!.constellation} · Nv ${s.suggestionData!.level}"
                            "${s.suggestionNeedsBuild ? " · ${l.t("teamsToBuild")}" : ""})"
                        : "🔒 ${s.character.name} — ${l.t("teamsNoSuggest")}",
                ],
              ),
            ],

            // ---- équipement (plus juste qu'une alerte ER) ----
            if (match.equipmentWarnings.isNotEmpty) ...[
              const SizedBox(height: 10),
              _InfoBlock(
                color: _cyan,
                lines: [
                  for (final s in match.equipmentWarnings)
                    s.noArtifacts
                        ? "🎒 ${s.character.name} — ${l.t("teamsNoArtifacts")}"
                        : "🗡 ${s.character.name} — ${l.t("teamsWeakWeapon")} (Nv ${s.buildInfo!.weaponLevel})",
                ],
              ),
            ],

            // ---- alertes de recharge ----
            if (match.erWarnings.isNotEmpty) ...[
              const SizedBox(height: 10),
              _InfoBlock(
                color: _amber,
                lines: [
                  for (final s in match.erWarnings)
                    "⚡ ${s.character.name} — ${l.t("teamsErEst")} ~${s.erValue!.round()} % "
                        "${l.t("teamsErAdvised")} ${s.slot.er} % ${l.t("teamsErNote")}",
                ],
              ),
            ],

            // ---- rotation + combos ----
            if (t.rotationSteps.isNotEmpty) ...[
              const SizedBox(height: 6),
              Theme(
                data: Theme.of(context)
                    .copyWith(dividerColor: Colors.transparent),
                child: ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  childrenPadding: const EdgeInsets.only(bottom: 8),
                  title: Row(
                    children: [
                      Icon(Icons.route, size: 16, color: cs.primary),
                      const SizedBox(width: 8),
                      Text(
                        "${l.t("teamsRotation")} (${t.rotation})",
                        style: const TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                  children: [
                    for (var i = 0; i < t.rotationSteps.length; i++)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 7),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 20,
                              height: 20,
                              decoration: BoxDecoration(
                                color: cs.primary.withValues(alpha: 0.18),
                                shape: BoxShape.circle,
                              ),
                              child: Center(
                                child: Text(
                                  "${i + 1}",
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w800,
                                    color: cs.primary,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                t.rotationSteps[i],
                                style: TextStyle(
                                  fontSize: 12.5,
                                  height: 1.5,
                                  color:
                                      Colors.white.withValues(alpha: 0.7),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    if (t.combos.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(Icons.tips_and_updates_outlined,
                                size: 15, color: cs.secondary),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                t.combos,
                                style: TextStyle(
                                  fontSize: 12,
                                  height: 1.5,
                                  fontStyle: FontStyle.italic,
                                  color:
                                      Colors.white.withValues(alpha: 0.55),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _modeLabel(String mode, L l) => switch (mode) {
        "abyss" => l.t("modeAbyss"),
        "theater" => l.t("modeTheater"),
        _ => l.t("modeOnslaught"),
      };
}

class _StatusBadge extends StatelessWidget {
  final TeamMatch match;
  final L l;
  const _StatusBadge({required this.match, required this.l});

  @override
  Widget build(BuildContext context) {
    final (color, text) = match.ready
        ? (_green, "✓ ${l.t("teamsReady")}")
        : match.complete
            ? (_cyan, "${l.t("teamsComplete")} · ${l.t("teamsToBuild")}")
            : (_amber,
                "${l.t("teamsMissingPrefix")} ${match.missing.length}");
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: Text(
        text,
        style: TextStyle(
            fontSize: 11, fontWeight: FontWeight.w800, color: color),
      ),
    );
  }
}

class _InfoBlock extends StatelessWidget {
  final Color color;
  final List<String> lines;
  const _InfoBlock({required this.color, required this.lines});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(11),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.09),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.32)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final t in lines)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Text(t,
                  style: const TextStyle(fontSize: 12, height: 1.45)),
            ),
        ],
      ),
    );
  }
}

class _SlotView extends StatelessWidget {
  final SlotMatch s;
  final L l;
  const _SlotView({required this.s, required this.l});

  @override
  Widget build(BuildContext context) {
    final owned = s.owned;
    final od = s.ownedData;
    final flagged = s.lowLevel || s.noArtifacts || s.weakWeapon;
    return SizedBox(
      width: 96,
      child: Column(
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              CharIcon(
                name: s.character.name,
                icon: s.character.icon,
                element: s.character.element,
                size: 56,
                dimmed: !owned,
                showName: false,
              ),
              if (s.viaAlt)
                Positioned(
                  top: -4,
                  right: -4,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 5, vertical: 2),
                    decoration: BoxDecoration(
                      color: _cyan,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      l.t("teamsAlt"),
                      style: const TextStyle(
                        fontSize: 8,
                        fontWeight: FontWeight.w900,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                ),
              if (!owned)
                const Positioned(
                  bottom: -2,
                  right: -2,
                  child: Text("🔒", style: TextStyle(fontSize: 13)),
                ),
              if (owned && s.noArtifacts)
                const Positioned(
                  bottom: -2,
                  right: -2,
                  child: Text("🎒", style: TextStyle(fontSize: 12)),
                ),
              if (owned && !s.noArtifacts && s.weakWeapon)
                const Positioned(
                  bottom: -2,
                  right: -2,
                  child: Text("🗡", style: TextStyle(fontSize: 12)),
                ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            s.character.name,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 11.5,
              fontWeight: FontWeight.w600,
              color: Colors.white.withValues(alpha: owned ? 0.9 : 0.4),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            owned
                ? "C${od!.constellation} · Nv ${od.level}"
                : l.t("teamsMissingChar"),
            style: TextStyle(
              fontSize: 10,
              color: !owned || flagged
                  ? _amber.withValues(alpha: 0.9)
                  : Colors.white.withValues(alpha: 0.5),
              fontWeight:
                  !owned || flagged ? FontWeight.w700 : FontWeight.normal,
            ),
          ),
          Text(
            s.slot.role,
            maxLines: 2,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 9.5,
              height: 1.25,
              color: Colors.white.withValues(alpha: 0.38),
            ),
          ),
        ],
      ),
    );
  }
}
