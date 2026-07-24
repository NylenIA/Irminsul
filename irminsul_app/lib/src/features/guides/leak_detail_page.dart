import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/element_backdrop.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/reveal.dart";

const _leakColor = Color(0xFFFF7B9C);

/// Fiche LEAK : contenu non confirmé, massivement étiqueté (docs/LEAK_POLICY).
class LeakDetailPage extends ConsumerWidget {
  final String id;
  const LeakDetailPage({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final leaks = ref.watch(leaksProvider);

    return leaks.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text("Erreur : $e")),
      data: (db) {
        final c = db.characters.where((x) => x.id == id).firstOrNull;
        if (c == null) return Center(child: Text(l.t("underConstruction")));
        final color = elementColor(c.element);

        return ElementBackdrop(
          element: c.element,
          intensity: 26,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(30),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Reveal(
                  child: TextButton.icon(
                    onPressed: () => context.go("/guides"),
                    icon: const Icon(Icons.arrow_back, size: 17),
                    label: Text(l.t("back")),
                  ),
                ),
                const SizedBox(height: 8),

                // ---- disclaimer géant ----
                Reveal(
                  delayMs: 40,
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: _leakColor.withValues(alpha: 0.10),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                          color: _leakColor.withValues(alpha: 0.4)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.warning_amber_rounded,
                            color: _leakColor),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            db.disclaimer,
                            style: const TextStyle(fontSize: 12.5, height: 1.5),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // ---- entête ----
                Reveal(
                  delayMs: 90,
                  child: GlassCard(
                    child: Row(
                      children: [
                        Container(
                          width: 84,
                          height: 84,
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(22),
                            border: Border.all(
                              color: _leakColor.withValues(alpha: 0.6),
                              width: 1.6,
                            ),
                          ),
                          child: Center(
                            child: Text(
                              "?",
                              style: TextStyle(
                                fontSize: 34,
                                fontWeight: FontWeight.w800,
                                color: color,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 20),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    c.name,
                                    style: const TextStyle(
                                        fontSize: 26,
                                        fontWeight: FontWeight.bold),
                                  ),
                                  const SizedBox(width: 10),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 10, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: _leakColor,
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Text(
                                      l.t("leakBadge"),
                                      style: const TextStyle(
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.w900,
                                        color: Color(0xFF3A0A18),
                                        letterSpacing: 0.8,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 5),
                              Text(
                                "${"★" * c.rarity} · ${c.weaponType} · ${c.kitVersion}",
                                style: TextStyle(
                                  fontSize: 13,
                                  color: color,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                "${l.t("leakExpected")} : ${c.expected}",
                                style: TextStyle(
                                  fontSize: 12.5,
                                  color: Colors.white.withValues(alpha: 0.65),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // ---- fiabilité ----
                Reveal(
                  delayMs: 140,
                  child: GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l.t("leakScore").toUpperCase(),
                          style: TextStyle(
                            fontSize: 11.5,
                            letterSpacing: 1.3,
                            fontWeight: FontWeight.w700,
                            color: Colors.white.withValues(alpha: 0.55),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(6),
                                child: LinearProgressIndicator(
                                  value: c.score / 100,
                                  minHeight: 9,
                                  backgroundColor:
                                      Colors.white.withValues(alpha: 0.07),
                                  valueColor:
                                      const AlwaysStoppedAnimation(_leakColor),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              "${c.score}/100",
                              style: const TextStyle(
                                  fontWeight: FontWeight.w800, fontSize: 14),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          c.grade,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white.withValues(alpha: 0.55),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // ---- résumé + kit rapporté ----
                Reveal(
                  delayMs: 190,
                  child: GlassCard(
                    child: Text(
                      c.summary,
                      style: TextStyle(
                        fontSize: 13,
                        height: 1.55,
                        color: Colors.white.withValues(alpha: 0.75),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                for (var i = 0; i < c.kit.length; i++)
                  Reveal(
                    delayMs: 230 + i * 60,
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: GlassCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              c.kit[i].title.toUpperCase(),
                              style: const TextStyle(
                                fontSize: 11,
                                letterSpacing: 1.2,
                                fontWeight: FontWeight.w700,
                                color: _leakColor,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              c.kit[i].desc,
                              style: TextStyle(
                                fontSize: 12.5,
                                height: 1.55,
                                color: Colors.white.withValues(alpha: 0.65),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                // ---- sources ----
                Reveal(
                  delayMs: 420,
                  child: GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l.t("leakSources").toUpperCase(),
                          style: TextStyle(
                            fontSize: 11.5,
                            letterSpacing: 1.3,
                            fontWeight: FontWeight.w700,
                            color: Colors.white.withValues(alpha: 0.55),
                          ),
                        ),
                        const SizedBox(height: 10),
                        for (final s in c.sources)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: Text(
                              "• ${s.name} — ${s.date}",
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.white.withValues(alpha: 0.6),
                              ),
                            ),
                          ),
                        const SizedBox(height: 4),
                        Text(
                          "${l.t("leakUpdated")} ${db.updated}",
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.white.withValues(alpha: 0.4),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
