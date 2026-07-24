import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/hover_card.dart";
import "../../widgets/reveal.dart";

/// « Gazette de Teyvat » : liste des fiches persos.
class GuidesPage extends ConsumerWidget {
  const GuidesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final chars = ref.watch(charactersProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Reveal(
            child: Text(
              l.t("navGuides"),
              style:
                  const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 4),
          Reveal(
            delayMs: 60,
            child: Text(
              l.t("guidesSubtitle"),
              style: TextStyle(color: Colors.white.withValues(alpha: 0.6)),
            ),
          ),
          const SizedBox(height: 24),
          chars.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => GlassCard(child: Text("Erreur fiches : $e")),
            data: (list) => Wrap(
              spacing: 16,
              runSpacing: 16,
              children: [
                for (var i = 0; i < list.length; i++)
                  Reveal(
                    delayMs: 100 + i * 80,
                    child: _CharCard(sheet: list[i]),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Reveal(
            delayMs: 400,
            child: Row(
              children: [
                Icon(Icons.science_outlined,
                    size: 14, color: Colors.white.withValues(alpha: 0.35)),
                const SizedBox(width: 6),
                Text(
                  l.t("curatedNote"),
                  style: TextStyle(
                    fontSize: 11.5,
                    color: Colors.white.withValues(alpha: 0.35),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CharCard extends StatelessWidget {
  final CharacterSheet sheet;
  const _CharCard({required this.sheet});

  @override
  Widget build(BuildContext context) {
    final color = elementColor(sheet.element);
    return HoverCard(
      glow: color,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => context.go("/guides/${sheet.id}"),
        child: SizedBox(
          width: 250,
          child: GlassCard(
            child: Row(
              children: [
                CharIcon(
                  name: sheet.name,
                  icon: sheet.icon,
                  element: sheet.element,
                  size: 56,
                  showName: false,
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            sheet.name,
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            "★" * sheet.rarity,
                            style: TextStyle(
                                fontSize: 9,
                                color: const Color(0xFFF2C14E)
                                    .withValues(alpha: 0.9)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        sheet.role,
                        style: TextStyle(
                          fontSize: 11.5,
                          color: Colors.white.withValues(alpha: 0.55),
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Icon(Icons.chevron_right,
                    color: Colors.white.withValues(alpha: 0.35)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
