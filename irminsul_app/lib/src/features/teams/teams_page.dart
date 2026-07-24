import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../data/meta_repository.dart";
import "../../data/team_matcher.dart";
import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/hover_card.dart";
import "../../widgets/reveal.dart";

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
          const SizedBox(height: 24),
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
                    final matches = matchTeams(
                        meta: db, box: playerBox, characters: list);
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Reveal(
                          child: _BoxChip(
                              count: playerBox.count,
                              label: playerBox.label,
                              l: l),
                        ),
                        const SizedBox(height: 18),
                        for (var i = 0; i < matches.length; i++) ...[
                          Reveal(
                            delayMs: 80 + i * 80,
                            child: _TeamMatchCard(
                                match: matches[i], l: l),
                          ),
                          const SizedBox(height: 16),
                        ],
                        Reveal(
                          delayMs: 100 + matches.length * 80,
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

// ------------------------------------------------------------------ cards --

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

class _TeamMatchCard extends StatelessWidget {
  final TeamMatch match;
  final L l;
  const _TeamMatchCard({required this.match, required this.l});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final t = match.team;
    final complete = match.complete;
    const green = Color(0xFF8BE28B);
    const amber = Color(0xFFF2C14E);

    return HoverCard(
      glow: complete ? cs.primary : Colors.white24,
      child: GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ---- entête ----
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
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 5),
                  decoration: BoxDecoration(
                    color: complete
                        ? green.withValues(alpha: 0.15)
                        : amber.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: (complete ? green : amber)
                          .withValues(alpha: 0.45),
                    ),
                  ),
                  child: Text(
                    complete
                        ? "✓ ${l.t("teamsComplete")}"
                        : "${l.t("teamsMissingPrefix")} ${match.missing.length}",
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: complete ? green : amber,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // ---- slots ----
            Wrap(
              spacing: 16,
              runSpacing: 12,
              children: [
                for (final s in match.slots) _SlotView(s: s, l: l),
              ],
            ),

            // ---- alertes ER ----
            if (match.slots.any((s) => s.erWarning)) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(11),
                decoration: BoxDecoration(
                  color: amber.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: amber.withValues(alpha: 0.35)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    for (final s in match.slots.where((x) => x.erWarning))
                      Text(
                        "⚡ ${s.character.name} — ${l.t("teamsErEst")} ~${s.erEstimate!.round()} % ${l.t("teamsErAdvised")} ${s.slot.er} %. ${l.t("teamsErNote")}",
                        style: const TextStyle(fontSize: 12, height: 1.5),
                      ),
                  ],
                ),
              ),
            ],

            // ---- rotation + combos ----
            if (t.rotationSteps.isNotEmpty) ...[
              const SizedBox(height: 8),
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

class _SlotView extends StatelessWidget {
  final SlotMatch s;
  final L l;
  const _SlotView({required this.s, required this.l});

  @override
  Widget build(BuildContext context) {
    final owned = s.owned;
    final od = s.ownedData;
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
                      color: const Color(0xFF22D3EE),
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
              color: owned
                  ? Colors.white.withValues(alpha: 0.5)
                  : const Color(0xFFF2C14E).withValues(alpha: 0.9),
              fontWeight: owned ? FontWeight.normal : FontWeight.w700,
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
