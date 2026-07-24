import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/reveal.dart";

/// Fiche perso complète (« Gazette de Teyvat »).
class GuideDetailPage extends ConsumerWidget {
  final String id;
  const GuideDetailPage({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final chars = ref.watch(charactersProvider);

    return chars.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text("Erreur : $e")),
      data: (list) {
        final sheet = list.where((c) => c.id == id).firstOrNull;
        if (sheet == null) {
          return Center(child: Text(l.t("underConstruction")));
        }
        final color = elementColor(sheet.element);

        return SingleChildScrollView(
          padding: const EdgeInsets.all(30),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ---- retour + entête ----
              Reveal(
                child: TextButton.icon(
                  onPressed: () => context.go("/guides"),
                  icon: const Icon(Icons.arrow_back, size: 17),
                  label: Text(l.t("back")),
                ),
              ),
              const SizedBox(height: 10),
              Reveal(
                delayMs: 60,
                child: GlassCard(
                  child: Row(
                    children: [
                      CharIcon(
                        name: sheet.name,
                        icon: sheet.icon,
                        element: sheet.element,
                        size: 84,
                        showName: false,
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  sheet.name,
                                  style: const TextStyle(
                                      fontSize: 26,
                                      fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(width: 10),
                                Text(
                                  "★" * sheet.rarity,
                                  style: const TextStyle(
                                      fontSize: 12, color: Color(0xFFF2C14E)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 5),
                            Text(
                              "${sheet.role} · ${sheet.weaponType}",
                              style: TextStyle(
                                fontSize: 13.5,
                                color: color,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              sheet.pitch,
                              style: TextStyle(
                                fontSize: 13,
                                height: 1.5,
                                color: Colors.white.withValues(alpha: 0.7),
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

              // ---- sections deux colonnes ----
              LayoutBuilder(builder: (context, cons) {
                final wide = cons.maxWidth > 760;
                final colW = wide ? (cons.maxWidth - 16) / 2 : cons.maxWidth;
                return Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    SizedBox(
                      width: colW,
                      child: Reveal(
                        delayMs: 140,
                        child: _Section(
                          icon: Icons.bolt,
                          color: color,
                          title: l.t("sectionTalents"),
                          child: Row(
                            children: [
                              for (var i = 0;
                                  i < sheet.talents.length;
                                  i++) ...[
                                if (i > 0)
                                  Padding(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 6),
                                    child: Icon(Icons.chevron_right,
                                        size: 16,
                                        color: Colors.white
                                            .withValues(alpha: 0.4)),
                                  ),
                                _Chip(text: sheet.talents[i], color: color),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: colW,
                      child: Reveal(
                        delayMs: 200,
                        child: _Section(
                          icon: Icons.gavel,
                          color: color,
                          title: l.t("sectionWeapons"),
                          child: Column(
                            children: [
                              for (final w in sheet.weapons)
                                _KV(k: w.name, v: w.note),
                            ],
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: colW,
                      child: Reveal(
                        delayMs: 260,
                        child: _Section(
                          icon: Icons.workspace_premium,
                          color: color,
                          title: l.t("sectionArtifacts"),
                          child: Column(
                            children: [
                              _KV(k: l.t("artifactSet"), v: sheet.artifacts.set),
                              _KV(k: l.t("artifactSands"), v: sheet.artifacts.sands),
                              _KV(k: l.t("artifactGoblet"), v: sheet.artifacts.goblet),
                              _KV(k: l.t("artifactCirclet"), v: sheet.artifacts.circlet),
                              _KV(k: l.t("artifactSubs"), v: sheet.artifacts.subs),
                            ],
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: colW,
                      child: Reveal(
                        delayMs: 320,
                        child: _Section(
                          icon: Icons.star_border,
                          color: color,
                          title: l.t("sectionConstellations"),
                          child: Column(
                            children: [
                              for (final c in sheet.constellations)
                                _KV(k: c.c, v: c.text),
                            ],
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: cons.maxWidth,
                      child: Reveal(
                        delayMs: 380,
                        child: _Section(
                          icon: Icons.inventory_2_outlined,
                          color: color,
                          title: l.t("sectionMaterials"),
                          child: Wrap(
                            spacing: 22,
                            runSpacing: 10,
                            children: [
                              _Mat(k: l.t("matGems"), v: sheet.materials.gems),
                              _Mat(k: l.t("matBoss"), v: sheet.materials.boss),
                              _Mat(k: l.t("matLocal"), v: sheet.materials.local),
                              _Mat(k: l.t("matCommon"), v: sheet.materials.common),
                              _Mat(k: l.t("matTalent"), v: sheet.materials.talent),
                              _Mat(k: l.t("matWeekly"), v: sheet.materials.weekly),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                );
              }),
            ],
          ),
        );
      },
    );
  }
}

class _Section extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final Widget child;
  const _Section({
    required this.icon,
    required this.color,
    required this.title,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 17, color: color),
              const SizedBox(width: 9),
              Text(
                title.toUpperCase(),
                style: TextStyle(
                  fontSize: 11.5,
                  letterSpacing: 1.3,
                  fontWeight: FontWeight.w700,
                  color: Colors.white.withValues(alpha: 0.55),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String text;
  final Color color;
  const _Chip({required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.13),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Text(text, style: const TextStyle(fontSize: 12.5)),
    );
  }
}

class _KV extends StatelessWidget {
  final String k;
  final String v;
  const _KV({required this.k, required this.v});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              k,
              style: TextStyle(
                fontSize: 12.5,
                fontWeight: FontWeight.w600,
                color: Colors.white.withValues(alpha: 0.85),
              ),
            ),
          ),
          Expanded(
            child: Text(
              v,
              style: TextStyle(
                fontSize: 12.5,
                height: 1.45,
                color: Colors.white.withValues(alpha: 0.6),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Mat extends StatelessWidget {
  final String k;
  final String v;
  const _Mat({required this.k, required this.v});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 200,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            k.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              letterSpacing: 1.1,
              color: Colors.white.withValues(alpha: 0.4),
            ),
          ),
          const SizedBox(height: 3),
          Text(v, style: const TextStyle(fontSize: 12.5)),
        ],
      ),
    );
  }
}
