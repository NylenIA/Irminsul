import "dart:io";

import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../i18n/strings.dart";
import "../../services/icon_cache.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/element_backdrop.dart";
import "../../widgets/game_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/gold_shimmer.dart";
import "../../widgets/reveal.dart";

/// Fiche perso complète : thème + animation de l'élément, sous-onglets
/// Build / Aptitudes / Constellations / Matériaux (données du jeu).
class GuideDetailPage extends ConsumerStatefulWidget {
  final String id;
  const GuideDetailPage({super.key, required this.id});

  @override
  ConsumerState<GuideDetailPage> createState() => _GuideDetailPageState();
}

class _GuideDetailPageState extends ConsumerState<GuideDetailPage> {
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    final l = L(ref.watch(localeProvider));
    final chars = ref.watch(charactersFullProvider);
    final builds = ref.watch(curatedBuildsProvider);

    return chars.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text("Erreur : $e")),
      data: (list) {
        final c = list.where((x) => x.id == widget.id).firstOrNull;
        if (c == null) {
          return Center(child: Text(l.t("underConstruction")));
        }
        final color = elementColor(c.element);
        final build = builds.maybeWhen(
          data: (m) => m[c.id],
          orElse: () => null,
        );

        final tabs = [
          l.t("tabBuild"),
          l.t("tabTalents"),
          l.t("tabCons"),
          l.t("tabMats"),
        ];

        return ElementBackdrop(
          element: c.element,
          intensity: c.rarity == 5 ? 38 : 24,
          golden: c.isArchon,
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

                // ---- entête héroïque (splash art + reflet 5★) ----
                Reveal(
                  delayMs: 50,
                  child: _HeroHeader(c: c, curated: build, color: color, l: l),
                ),
                const SizedBox(height: 16),

                // ---- sous-onglets ----
                Reveal(
                  delayMs: 100,
                  child: Row(
                    children: [
                      for (var i = 0; i < tabs.length; i++)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: InkWell(
                            borderRadius: BorderRadius.circular(11),
                            onTap: () => setState(() => _tab = i),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 220),
                              curve: Curves.easeOutCubic,
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 18, vertical: 9),
                              decoration: BoxDecoration(
                                color: _tab == i
                                    ? color.withValues(alpha: 0.85)
                                    : Colors.white.withValues(alpha: 0.045),
                                borderRadius: BorderRadius.circular(11),
                                border: _tab == i
                                    ? null
                                    : Border.all(
                                        color: Colors.white
                                            .withValues(alpha: 0.09)),
                                boxShadow: _tab == i
                                    ? [
                                        BoxShadow(
                                          color:
                                              color.withValues(alpha: 0.35),
                                          blurRadius: 18,
                                          offset: const Offset(0, 6),
                                        ),
                                      ]
                                    : const [],
                              ),
                              child: Text(
                                tabs[i],
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: _tab == i
                                      ? FontWeight.w700
                                      : FontWeight.normal,
                                  color: _tab == i
                                      ? Colors.black.withValues(alpha: 0.85)
                                      : Colors.white70,
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),

                // ---- contenu de l'onglet ----
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 280),
                  switchInCurve: Curves.easeOutCubic,
                  child: switch (_tab) {
                    0 => _BuildTab(
                        key: const ValueKey(0), c: c, curated: build, l: l),
                    1 => _TalentsTab(key: const ValueKey(1), c: c, l: l),
                    2 => _ConsTab(key: const ValueKey(2), c: c, l: l),
                    _ => _MatsTab(key: const ValueKey(3), c: c, l: l),
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

// ------------------------------------------------------------ Entête héro --

class _HeroHeader extends StatelessWidget {
  final CharacterFull c;
  final CuratedBuild? curated;
  final Color color;
  final L l;
  const _HeroHeader({
    required this.c,
    required this.curated,
    required this.color,
    required this.l,
  });

  @override
  Widget build(BuildContext context) {
    final core = Container(
      height: 168,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.045),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: c.rarity == 5
              ? const Color(0xFFF6D27A).withValues(alpha: 0.35)
              : Colors.white.withValues(alpha: 0.09),
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // splash art gacha en fond (fondu vers la gauche)
          if (c.splash.isNotEmpty)
            Positioned.fill(
              child: FutureBuilder<File?>(
                future: IconCache.get(c.splash),
                builder: (context, snap) {
                  if (snap.data == null) return const SizedBox.shrink();
                  return ShaderMask(
                    shaderCallback: (r) => const LinearGradient(
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
                      colors: [
                        Colors.transparent,
                        Colors.black45,
                        Colors.black,
                      ],
                      stops: [0.15, 0.45, 0.8],
                    ).createShader(r),
                    blendMode: BlendMode.dstIn,
                    child: Image.file(
                      snap.data!,
                      fit: BoxFit.cover,
                      alignment: const Alignment(0.4, -0.4),
                      opacity: const AlwaysStoppedAnimation(0.55),
                    ),
                  );
                },
              ),
            ),
          // contenu
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                CharIcon(
                  name: c.name,
                  icon: c.icon,
                  element: c.element,
                  size: 92,
                  showName: false,
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            c.name,
                            style: const TextStyle(
                                fontSize: 27, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(width: 10),
                          Text(
                            "★" * c.rarity,
                            style: const TextStyle(
                                fontSize: 12, color: Color(0xFFF2C14E)),
                          ),
                          if (c.isArchon) ...[
                            const SizedBox(width: 10),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(colors: [
                                  Color(0xFFF6D27A),
                                  Color(0xFFE9B84C),
                                ]),
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: Text(
                                "👑 ${l.t("archonBadge")}",
                                style: const TextStyle(
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF3A2C08),
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 5),
                      Text(
                        [
                          if (c.title.isNotEmpty) c.title,
                          c.weaponType,
                          if (c.region.isNotEmpty) c.region,
                        ].join(" · "),
                        style: TextStyle(
                          fontSize: 13,
                          color: color,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (curated != null) ...[
                        const SizedBox(height: 6),
                        Text(
                          curated!.role,
                          style: TextStyle(
                            fontSize: 12.5,
                            color: Colors.white.withValues(alpha: 0.8),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );

    // 5★ : reflet doré qui balaye la carte.
    return c.rarity == 5 ? GoldShimmer(child: core) : core;
  }
}

// ------------------------------------------------------------------ Build --

class _BuildTab extends StatelessWidget {
  final CharacterFull c;
  final CuratedBuild? curated;
  final L l;
  const _BuildTab(
      {super.key, required this.c, required this.curated, required this.l});

  @override
  Widget build(BuildContext context) {
    final color = elementColor(c.element);
    final b = curated;
    if (b == null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (c.description.isNotEmpty)
            Reveal(
              child: GlassCard(
                child: Text(
                  c.description,
                  style: TextStyle(
                    fontSize: 13,
                    height: 1.55,
                    color: Colors.white.withValues(alpha: 0.7),
                  ),
                ),
              ),
            ),
          const SizedBox(height: 14),
          Reveal(
            delayMs: 80,
            child: GlassCard(
              child: Row(
                children: [
                  Icon(Icons.pending_outlined, color: color),
                  const SizedBox(width: 14),
                  Expanded(child: Text(l.t("buildSoon"))),
                ],
              ),
            ),
          ),
        ],
      );
    }

    return LayoutBuilder(builder: (context, cons) {
      final wide = cons.maxWidth > 760;
      final colW = wide ? (cons.maxWidth - 16) / 2 : cons.maxWidth;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Reveal(
            child: GlassCard(
              child: Text(
                b.pitch,
                style: TextStyle(
                  fontSize: 13,
                  height: 1.55,
                  color: Colors.white.withValues(alpha: 0.75),
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 16,
            runSpacing: 16,
            children: [
              SizedBox(
                width: colW,
                child: Reveal(
                  delayMs: 70,
                  child: _Section(
                    icon: Icons.bolt,
                    color: color,
                    title: l.t("sectionTalents"),
                    child: Row(
                      children: [
                        for (var i = 0; i < b.talentPriority.length; i++) ...[
                          if (i > 0)
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 6),
                              child: Icon(Icons.chevron_right,
                                  size: 16,
                                  color:
                                      Colors.white.withValues(alpha: 0.4)),
                            ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 7),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.13),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                  color: color.withValues(alpha: 0.35)),
                            ),
                            child: Text(b.talentPriority[i],
                                style: const TextStyle(fontSize: 12.5)),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
              SizedBox(
                width: colW,
                child: Reveal(
                  delayMs: 120,
                  child: _Section(
                    icon: Icons.gavel,
                    color: color,
                    title: l.t("sectionWeapons"),
                    child: Column(
                      children: [
                        for (final w in b.weapons)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: Row(
                              children: [
                                GameIcon(
                                    filename: w.icon,
                                    size: 40,
                                    fallback: Icons.gavel,
                                    tint: color),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(w.name,
                                          style: const TextStyle(
                                              fontSize: 13.5,
                                              fontWeight: FontWeight.w600)),
                                      Text(
                                        w.note,
                                        style: TextStyle(
                                          fontSize: 11.5,
                                          color: Colors.white
                                              .withValues(alpha: 0.5),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
              SizedBox(
                width: colW,
                child: Reveal(
                  delayMs: 170,
                  child: _Section(
                    icon: Icons.workspace_premium,
                    color: color,
                    title: l.t("sectionArtifacts"),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            GameIcon(
                                filename: b.artifacts.setIcon,
                                size: 40,
                                fallback: Icons.workspace_premium,
                                tint: color),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                b.artifacts.setName,
                                style: const TextStyle(
                                    fontSize: 13.5,
                                    fontWeight: FontWeight.w600),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        _KV(k: l.t("artifactSands"), v: b.artifacts.sands),
                        _KV(k: l.t("artifactGoblet"), v: b.artifacts.goblet),
                        _KV(k: l.t("artifactCirclet"), v: b.artifacts.circlet),
                        _KV(k: l.t("artifactSubs"), v: b.artifacts.subs),
                      ],
                    ),
                  ),
                ),
              ),
              SizedBox(
                width: colW,
                child: Reveal(
                  delayMs: 220,
                  child: _Section(
                    icon: Icons.star_border,
                    color: color,
                    title: l.t("sectionConstellations"),
                    child: Column(
                      children: [
                        for (final k in b.constellations)
                          _KV(k: k.c, v: k.text),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Reveal(
            delayMs: 280,
            child: Text(
              l.t("curatedNote"),
              style: TextStyle(
                fontSize: 11.5,
                color: Colors.white.withValues(alpha: 0.35),
              ),
            ),
          ),
        ],
      );
    });
  }
}

// -------------------------------------------------------------- Aptitudes --

class _TalentsTab extends StatelessWidget {
  final CharacterFull c;
  final L l;
  const _TalentsTab({super.key, required this.c, required this.l});

  @override
  Widget build(BuildContext context) {
    final color = elementColor(c.element);
    return Column(
      children: [
        for (var i = 0; i < c.talents.length; i++)
          Reveal(
            delayMs: 50 + i * 60,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: GlassCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        GameIcon(
                            filename: c.talents[i].icon,
                            size: 46,
                            fallback: Icons.bolt,
                            tint: color),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                c.talents[i].slot.toUpperCase(),
                                style: TextStyle(
                                  fontSize: 10.5,
                                  letterSpacing: 1.2,
                                  color: color,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              const SizedBox(height: 3),
                              Text(
                                c.talents[i].name,
                                style: const TextStyle(
                                    fontSize: 15.5,
                                    fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    if (c.talents[i].desc.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Text(
                        c.talents[i].desc,
                        style: TextStyle(
                          fontSize: 12.5,
                          height: 1.55,
                          color: Colors.white.withValues(alpha: 0.65),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

// --------------------------------------------------------- Constellations --

class _ConsTab extends StatelessWidget {
  final CharacterFull c;
  final L l;
  const _ConsTab({super.key, required this.c, required this.l});

  @override
  Widget build(BuildContext context) {
    final color = elementColor(c.element);
    return Column(
      children: [
        for (var i = 0; i < c.cons.length; i++)
          Reveal(
            delayMs: 50 + i * 60,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: GlassCard(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Column(
                      children: [
                        GameIcon(
                            filename: c.cons[i].icon,
                            size: 46,
                            fallback: Icons.star_border,
                            tint: color),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            "C${c.cons[i].n}",
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              color: color,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            c.cons[i].name,
                            style: const TextStyle(
                                fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            c.cons[i].desc,
                            style: TextStyle(
                              fontSize: 12.5,
                              height: 1.55,
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
          ),
      ],
    );
  }
}

// -------------------------------------------------------------- Matériaux --

class _MatsTab extends StatelessWidget {
  final CharacterFull c;
  final L l;
  const _MatsTab({super.key, required this.c, required this.l});

  @override
  Widget build(BuildContext context) {
    final color = elementColor(c.element);
    Widget chips(List<MatEntry> items) => Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            for (final m in items)
              Container(
                width: 220,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(13),
                  border:
                      Border.all(color: Colors.white.withValues(alpha: 0.10)),
                ),
                child: Row(
                  children: [
                    GameIcon(
                      filename: m.icon,
                      size: 40,
                      fallback: Icons.category_outlined,
                      tint: color,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        m.name,
                        style: const TextStyle(fontSize: 12, height: 1.3),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      "×${m.qty}",
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                        color: color,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Reveal(
          child: _Section(
            icon: Icons.trending_up,
            color: color,
            title: l.t("matAsc"),
            child: chips(c.matAscension),
          ),
        ),
        const SizedBox(height: 16),
        Reveal(
          delayMs: 90,
          child: _Section(
            icon: Icons.menu_book,
            color: color,
            title: l.t("matTal"),
            child: chips(c.matTalents),
          ),
        ),
        const SizedBox(height: 12),
        Reveal(
          delayMs: 160,
          child: Text(
            l.t("gameDataNote"),
            style: TextStyle(
              fontSize: 11.5,
              color: Colors.white.withValues(alpha: 0.35),
            ),
          ),
        ),
      ],
    );
  }
}

// ------------------------------------------------------------------ utils --

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
            width: 100,
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
