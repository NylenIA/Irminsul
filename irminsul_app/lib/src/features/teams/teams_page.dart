import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../data/characters_repository.dart";
import "../../data/meta_repository.dart";
import "../../data/team_matcher.dart";
import "../../i18n/strings.dart";
import "../../services/gcsim_service.dart";
import "../../services/sim_cache.dart";
import "../../state/providers.dart";
import "../../widgets/content_banner.dart";
import "team_creator_page.dart"
    show showSimInfoDialog, CustomTeam, customTeamsProvider;
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/hover_card.dart";
import "../../widgets/reveal.dart";
import "../../widgets/sim_breakdown.dart";

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
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    l.t("teamsSubtitle"),
                    style:
                        TextStyle(color: Colors.white.withValues(alpha: 0.6)),
                  ),
                ),
                FilledButton.icon(
                  onPressed: () => context.go("/teams/create"),
                  icon: const Icon(Icons.add, size: 18),
                  label: Text(l.t("creatorOpen")),
                ),
              ],
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
                    final byId = {for (final c in list) c.id: c};
                    final all = matchTeams(
                        meta: db, box: playerBox, characters: list);
                    final mc =
                        mode == null ? null : db.content?.byMode[mode];
                    final forMode = mode == null
                        ? all
                        : all
                            .where((m) => m.team.servesMode(mode))
                            .toList();
                    // Théâtre : on masque ce que la saison interdit.
                    final shown = filterBySeason<TeamMatch>(
                        forMode, mc, (m) => m.team.chars);
                    final hidden = forMode.length - shown.length;
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

                        // ---- contenu ACTUEL du mode sélectionné ----
                        if (mode != null && db.content != null) ...[
                          Reveal(
                            delayMs: 50,
                            child: ContentBanner(
                              mode: mode,
                              content: db.content!,
                              bestTeamName: shown.isNotEmpty
                                  ? shown.first.team.name
                                  : null,
                              l: l,
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],

                        if (hidden > 0) ...[
                          Reveal(
                            delayMs: 55,
                            child: Row(
                              children: [
                                Icon(Icons.filter_alt_outlined,
                                    size: 14, color: _amber),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    "$hidden ${l.t("seasonHidden")}",
                                    style: TextStyle(
                                        fontSize: 11.5,
                                        color:
                                            _amber.withValues(alpha: 0.85)),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 12),
                        ],

                        // ---- tes équipes créées (créateur) ----
                        _CustomTeamsSection(l: l, mode: mode),

                        for (var i = 0; i < shown.length; i++) ...[
                          Reveal(
                            delayMs: 60 + (i.clamp(0, 8)) * 70,
                            child: _TeamMatchCard(
                                match: shown[i],
                                l: l,
                                byId: byId,
                                boxLabel: playerBox.label),
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

/// Tes équipes créées dans le créateur, classées par mode.
class _CustomTeamsSection extends ConsumerWidget {
  final L l;
  final String? mode;
  const _CustomTeamsSection({required this.l, required this.mode});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cs = Theme.of(context).colorScheme;
    final chars = ref.watch(charactersFullProvider).maybeWhen(
          data: (list) => {for (final c in list) c.good: c},
          orElse: () => <String, CharacterFull>{},
        );
    final teams = ref.watch(customTeamsProvider).maybeWhen(
          data: (t) => t,
          orElse: () => const <CustomTeam>[],
        );
    final shown =
        mode == null ? teams : teams.where((t) => t.mode == mode).toList();
    if (shown.isEmpty) return const SizedBox.shrink();

    String modeLabel(String m) => switch (m) {
          "abyss" => l.t("modeAbyss"),
          "theater" => l.t("modeTheater"),
          _ => l.t("modeOnslaught"),
        };

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Reveal(
        child: GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.bookmark, size: 16, color: cs.secondary),
                  const SizedBox(width: 8),
                  Text(
                    l.t("teamsMyCreated").toUpperCase(),
                    style: TextStyle(
                      fontSize: 11,
                      letterSpacing: 1.3,
                      fontWeight: FontWeight.w800,
                      color: Colors.white.withValues(alpha: 0.55),
                    ),
                  ),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: () => context.go("/teams/create"),
                    icon: const Icon(Icons.edit, size: 15),
                    label: Text(l.t("creatorOpenIn")),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  for (final t in shown)
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.05),
                        borderRadius: BorderRadius.circular(13),
                        border: Border.all(
                            color: Colors.white.withValues(alpha: 0.10)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          for (final k in t.chars)
                            if (chars[k] != null)
                              Padding(
                                padding: const EdgeInsets.only(right: 4),
                                child: CharIcon(
                                  name: chars[k]!.name,
                                  icon: chars[k]!.icon,
                                  element: chars[k]!.element,
                                  size: 28,
                                  showName: false,
                                ),
                              ),
                          const SizedBox(width: 8),
                          ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 170),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(t.name,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                        fontSize: 12.5,
                                        fontWeight: FontWeight.w700)),
                                Text(
                                  "${modeLabel(t.mode)}${t.lastDps != null ? " · ${t.lastDps} DPS" : ""}",
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                    fontSize: 10.5,
                                    color: cs.primary,
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
            ],
          ),
        ),
      ),
    );
  }
}

class _TeamMatchCard extends StatelessWidget {
  final TeamMatch match;
  final L l;
  final Map<String, CharacterFull> byId;
  final String boxLabel;
  const _TeamMatchCard(
      {required this.match,
      required this.l,
      required this.byId,
      required this.boxLabel});

  /// Adapte le template gcsim à la BOX : si un slot est pourvu par une
  /// ALTERNATIVE, on substitue le perso dans la liste ET dans la rotation.
  /// Sans ça, la sim échouerait « personnage absent » sur une équipe
  /// affichée COMPLÈTE.
  (GcsimTemplateData, String?) _effectiveTemplate(GcsimTemplateData tpl) {
    var rotation = tpl.rotation;
    final chars = List<String>.from(tpl.chars);
    final notes = <String>[];
    for (final s in match.slots) {
      final titular = byId[s.slot.id];
      if (titular == null || s.character.id == s.slot.id) continue;
      final oldName = GcsimService.gcsimName(titular.good);
      final newName = GcsimService.gcsimName(s.character.good);
      rotation =
          rotation.replaceAll(RegExp("\\b$oldName\\b"), newName);
      final idx = chars.indexOf(titular.good);
      if (idx >= 0) chars[idx] = s.character.good;
      notes.add("${titular.name} → ${s.character.name}");
    }
    return (
      GcsimTemplateData(chars, rotation),
      notes.isEmpty ? null : notes.join(" · "),
    );
  }

  /// Substitutions réellement appliquées (titulaire → remplaçant joué).
  Map<String, String> get _substitutions => {
        for (final s in match.slots)
          if (byId[s.slot.id] != null && s.character.id != s.slot.id)
            byId[s.slot.id]!.name: s.character.name,
      };

  /// Réécrit un texte de rotation/combo avec les persos RÉELLEMENT joués.
  /// Sans ça l'app disait « Zhongli E » alors que Zhongli n'est pas dans
  /// l'équipe affichée (il est remplacé par Xilonen) : conseil injouable.
  String _adaptText(String text, Map<String, String> subs) {
    var out = text;
    subs.forEach((from, to) {
      out = out.replaceAll(RegExp("\\b${RegExp.escape(from)}\\b"), to);
    });
    return out;
  }

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
                for (final s in match.slots)
                  _SlotView(
                      s: s,
                      l: l,
                      replaces: s.viaAlt ? byId[s.slot.id]?.name : null),
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

            // ---- simulation gcsim (vrai DPS sur les builds du joueur) ----
            if (t.gcsim != null && match.complete) ...[
              const SizedBox(height: 12),
              Builder(builder: (context) {
                final (tpl, adaptNote) = _effectiveTemplate(t.gcsim!);
                return _SimSection(
                    template: tpl,
                    l: l,
                    adaptNote: adaptNote,
                    teamId: t.id,
                    boxLabel: boxLabel);
              }),
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
                                _adaptText(
                                    t.rotationSteps[i], _substitutions),
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
                                _adaptText(t.combos, _substitutions),
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

/// Bouton + résultat de la simulation gcsim sur les builds réels du joueur.
class _SimSection extends ConsumerStatefulWidget {
  final GcsimTemplateData template;
  final L l;
  final String? adaptNote; // substitutions box (ex. « Xingqiu → Yelan »)
  final String teamId;
  final String boxLabel;
  const _SimSection(
      {required this.template,
      required this.l,
      this.adaptNote,
      required this.teamId,
      required this.boxLabel});

  @override
  ConsumerState<_SimSection> createState() => _SimSectionState();
}

class _SimSectionState extends ConsumerState<_SimSection> {
  bool _running = false;
  SimResult? _result;
  String? _error;

  Future<void> _run() async {
    setState(() {
      _running = true;
      _error = null;
    });
    try {
      final r = await GcsimService.run(
        GcsimTemplate(widget.template.chars, widget.template.rotation),
      );
      // mémorise le VRAI résultat pour cette box → le dashboard l'affiche
      await SimCache.put(widget.teamId, r, widget.boxLabel);
      ref.invalidate(simCacheProvider);
      if (mounted) setState(() => _result = r);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _running = false);
    }
  }

  static String _fmt(num v) {
    final s = v.round().toString();
    final b = StringBuffer();
    for (var i = 0; i < s.length; i++) {
      if (i > 0 && (s.length - i) % 3 == 0) b.write(" ");
      b.write(s[i]);
    }
    return b.toString();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final l = widget.l;

    if (_result != null) {
      final r = _result!;
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          gradient: LinearGradient(colors: [
            cs.primary.withValues(alpha: 0.14),
            cs.tertiary.withValues(alpha: 0.08),
          ]),
          borderRadius: BorderRadius.circular(13),
          border: Border.all(color: cs.primary.withValues(alpha: 0.4)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.bolt, color: cs.primary),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            _fmt(r.dps),
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w800,
                              color: cs.primary,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Padding(
                            padding: const EdgeInsets.only(bottom: 3),
                            child: Text(
                              "${l.t("simDpsLabel")} · "
                              "min ${_fmt(r.dpsMin)} / max ${_fmt(r.dpsMax)}",
                              style: TextStyle(
                                fontSize: 11.5,
                                color: Colors.white.withValues(alpha: 0.6),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        "${r.iterations} ${l.t("simNote")}",
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.white.withValues(alpha: 0.45),
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  tooltip: l.t("simHowTitle"),
                  icon: Icon(Icons.info_outline,
                      size: 18,
                      color: Colors.white.withValues(alpha: 0.55)),
                  onPressed: () => showSimInfoDialog(context, l),
                ),
                TextButton(
                  onPressed: _running ? null : _run,
                  child: Text(l.t("simAgain")),
                ),
              ],
            ),
            if (widget.adaptNote != null) ...[
              const SizedBox(height: 6),
              Text(
                "${l.t("simAdapted")} ${widget.adaptNote}",
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.white.withValues(alpha: 0.5),
                ),
              ),
            ],
            const SizedBox(height: 10),
            SimBreakdown(result: r),
          ],
        ),
      );
    }

    return Row(
      children: [
        FilledButton.icon(
          onPressed: _running ? null : _run,
          icon: _running
              ? const SizedBox(
                  width: 15,
                  height: 15,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.speed, size: 18),
          label: Text(_running ? l.t("simRunning") : l.t("simButton")),
        ),
        if (_error != null) ...[
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _error!,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 11.5, color: _amber),
            ),
          ),
        ],
      ],
    );
  }
}

class _SlotView extends StatelessWidget {
  final SlotMatch s;
  final L l;

  /// Nom du titulaire quand ce slot est joué par une alternative — affiché
  /// pour qu'on sache QUI est remplacé (sinon la rotation semble parler d'un
  /// perso absent de l'équipe).
  final String? replaces;
  const _SlotView({required this.s, required this.l, this.replaces});

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
          if (replaces != null)
            Text(
              "${l.t("teamsReplaces")} $replaces",
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 9.5,
                height: 1.3,
                fontWeight: FontWeight.w700,
                color: _cyan,
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
