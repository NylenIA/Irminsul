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

final _searchProvider = StateProvider<String>((ref) => "");
final _elementFilterProvider = StateProvider<String?>((ref) => null);

/// « Gazette de Teyvat » : tous les personnages du jeu (données genshin-db).
class GuidesPage extends ConsumerWidget {
  const GuidesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final chars = ref.watch(charactersFullProvider);
    final query = ref.watch(_searchProvider).toLowerCase();
    final elementFilter = ref.watch(_elementFilterProvider);

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
            delayMs: 50,
            child: Text(
              l.t("guidesSubtitle"),
              style: TextStyle(color: Colors.white.withValues(alpha: 0.6)),
            ),
          ),
          const SizedBox(height: 20),

          // ---- recherche + filtres élément ----
          Reveal(
            delayMs: 90,
            child: Row(
              children: [
                SizedBox(
                  width: 280,
                  child: TextField(
                    onChanged: (v) =>
                        ref.read(_searchProvider.notifier).state = v,
                    decoration: InputDecoration(
                      hintText: l.t("searchHint"),
                      prefixIcon: const Icon(Icons.search, size: 19),
                      filled: true,
                      fillColor: Colors.white.withValues(alpha: 0.05),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                for (final e in const [
                  "pyro", "hydro", "electro", "cryo", "anemo", "geo", "dendro"
                ])
                  _ElementDot(
                    element: e,
                    active: elementFilter == e,
                    onTap: () => ref
                        .read(_elementFilterProvider.notifier)
                        .state = elementFilter == e ? null : e,
                  ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          chars.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => GlassCard(child: Text("Erreur fiches : $e")),
            data: (list) {
              final filtered = list.where((c) {
                if (elementFilter != null && c.element != elementFilter) {
                  return false;
                }
                if (query.isNotEmpty &&
                    !c.name.toLowerCase().contains(query)) {
                  return false;
                }
                return true;
              }).toList()
                ..sort((a, b) {
                  final r = b.rarity.compareTo(a.rarity);
                  return r != 0 ? r : a.name.compareTo(b.name);
                });
              return Wrap(
                spacing: 14,
                runSpacing: 14,
                children: [
                  for (var i = 0; i < filtered.length; i++)
                    Reveal(
                      delayMs: 60 + (i % 12) * 40,
                      child: _CharCard(c: filtered[i]),
                    ),
                ],
              );
            },
          ),
          const SizedBox(height: 16),
          Reveal(
            delayMs: 300,
            child: Row(
              children: [
                Icon(Icons.verified_outlined,
                    size: 14, color: Colors.white.withValues(alpha: 0.35)),
                const SizedBox(width: 6),
                Text(
                  l.t("gameDataNote"),
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

class _ElementDot extends StatelessWidget {
  final String element;
  final bool active;
  final VoidCallback onTap;
  const _ElementDot({
    required this.element,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = elementColor(element);
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: active ? 0.9 : 0.22),
            border: Border.all(
                color: color.withValues(alpha: active ? 1 : 0.4),
                width: active ? 2 : 1),
            boxShadow: active
                ? [BoxShadow(color: color.withValues(alpha: 0.5), blurRadius: 10)]
                : const [],
          ),
        ),
      ),
    );
  }
}

class _CharCard extends StatelessWidget {
  final CharacterFull c;
  const _CharCard({required this.c});

  @override
  Widget build(BuildContext context) {
    final color = elementColor(c.element);
    return HoverCard(
      glow: color,
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () => context.go("/guides/${c.id}"),
        child: Container(
          width: 108,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.045),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: Colors.white.withValues(alpha: 0.09)),
          ),
          child: Column(
            children: [
              CharIcon(
                name: c.name,
                icon: c.icon,
                element: c.element,
                size: 64,
                showName: false,
              ),
              const SizedBox(height: 8),
              Text(
                c.name,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                    fontSize: 12.5, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 3),
              Text(
                "★" * c.rarity,
                style: TextStyle(
                  fontSize: 8,
                  color: const Color(0xFFF2C14E)
                      .withValues(alpha: c.rarity == 5 ? 0.95 : 0.55),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
