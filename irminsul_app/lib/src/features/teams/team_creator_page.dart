import "dart:convert";

import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";
import "package:shared_preferences/shared_preferences.dart";

import "../../data/characters_repository.dart";
import "../../i18n/strings.dart";
import "../../services/box_service.dart";
import "../../services/gcsim_service.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/char_icon.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/reveal.dart";
import "../../widgets/sim_breakdown.dart";

const _amber = Color(0xFFF2C14E);

/// Une étape de rotation créée par le joueur.
class RotationStep {
  final String goodKey; // perso (clé GOOD)
  final String action; // skill | burst | charge | attack
  final int count; // pour attack

  const RotationStep(this.goodKey, this.action, [this.count = 2]);

  Map<String, dynamic> toJson() => {"c": goodKey, "a": action, "n": count};
  static RotationStep fromJson(Map<String, dynamic> m) => RotationStep(
      m["c"] as String, m["a"] as String, (m["n"] as num?)?.toInt() ?? 2);
}

/// Équipe créée par le joueur (persistée localement).
class CustomTeam {
  final String name;
  final List<String> chars; // clés GOOD (4)
  final List<RotationStep> steps;
  final int? lastDps;
  final String mode; // abyss | theater | onslaught

  const CustomTeam({
    required this.name,
    required this.chars,
    required this.steps,
    this.lastDps,
    this.mode = "abyss",
  });

  Map<String, dynamic> toJson() => {
        "name": name,
        "chars": chars,
        "steps": steps.map((s) => s.toJson()).toList(),
        "lastDps": lastDps,
        "mode": mode,
      };
  static CustomTeam fromJson(Map<String, dynamic> m) => CustomTeam(
        name: m["name"] as String,
        chars: (m["chars"] as List).cast<String>(),
        steps: (m["steps"] as List)
            .map((s) => RotationStep.fromJson(s as Map<String, dynamic>))
            .toList(),
        lastDps: (m["lastDps"] as num?)?.toInt(),
        mode: m["mode"] as String? ?? "abyss",
      );
}

/// Équipes créées par le joueur (rechargées à la demande ; invalider après
/// sauvegarde/suppression).
final customTeamsProvider =
    FutureProvider<List<CustomTeam>>((ref) => loadCustomTeams());

Future<List<CustomTeam>> loadCustomTeams() async {
  final prefs = await SharedPreferences.getInstance();
  final raw = prefs.getString("custom_teams");
  if (raw == null) return [];
  try {
    return (jsonDecode(raw) as List)
        .map((m) => CustomTeam.fromJson(m as Map<String, dynamic>))
        .toList();
  } catch (_) {
    return [];
  }
}

Future<void> saveCustomTeams(List<CustomTeam> teams) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(
      "custom_teams", jsonEncode(teams.map((t) => t.toJson()).toList()));
}

/// Convertit les étapes en script gcsim (boucle infinie).
String buildRotationScript(
    List<RotationStep> steps, String Function(String) gname) {
  final buf = StringBuffer("while 1 {\n");
  for (final s in steps) {
    final n = gname(s.goodKey);
    switch (s.action) {
      case "attack":
        buf.writeln("    $n attack:${s.count};");
      default:
        buf.writeln("    $n ${s.action};");
    }
  }
  buf.write("}");
  return buf.toString();
}

/// « Créer ma team » : 4 persos de TA box, rotation à construire, vrai DPS.
class TeamCreatorPage extends ConsumerStatefulWidget {
  const TeamCreatorPage({super.key});

  @override
  ConsumerState<TeamCreatorPage> createState() => _TeamCreatorPageState();
}

class _TeamCreatorPageState extends ConsumerState<TeamCreatorPage> {
  final List<String> _picked = []; // clés GOOD
  final List<RotationStep> _steps = [];
  String _search = "";
  String? _activeChar; // perso sélectionné pour ajouter des étapes
  int _atkCount = 2; // nombre d'attaques normales par étape (1..8)
  String _mode = "abyss"; // mode visé (abyss | theater | onslaught)
  final _nameCtrl = TextEditingController();

  bool _running = false;
  SimResult? _result;
  String? _error;

  List<CustomTeam> _saved = [];

  @override
  void initState() {
    super.initState();
    loadCustomTeams().then((t) {
      if (mounted) setState(() => _saved = t);
    });
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  // clé GOOD -> nom gcsim (repris de GcsimService via la config générée)
  Future<void> _simulate() async {
    if (_picked.length != 4 || _steps.isEmpty) return;
    setState(() {
      _running = true;
      _error = null;
      _result = null;
    });
    try {
      final script = buildRotationScript(
          _steps, (k) => GcsimService.gcsimName(k));
      final r = await GcsimService.run(GcsimTemplate(_picked, script));
      if (mounted) setState(() => _result = r);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _running = false);
    }
  }

  Future<void> _save(L l) async {
    final name = _nameCtrl.text.trim().isEmpty
        ? l.t("creatorDefaultName")
        : _nameCtrl.text.trim();
    final team = CustomTeam(
      name: name,
      chars: List.of(_picked),
      steps: List.of(_steps),
      lastDps: _result?.dps,
      mode: _mode,
    );
    final updated = [..._saved.where((t) => t.name != name), team];
    await saveCustomTeams(updated);
    ref.invalidate(customTeamsProvider);
    if (mounted) setState(() => _saved = updated);
  }

  void _loadTeam(CustomTeam t) {
    setState(() {
      _picked
        ..clear()
        ..addAll(t.chars);
      _steps
        ..clear()
        ..addAll(t.steps);
      _nameCtrl.text = t.name;
      _activeChar = t.chars.first;
      _mode = t.mode;
      _result = null;
      _error = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final l = L(ref.watch(localeProvider));
    final cs = Theme.of(context).colorScheme;
    final box = ref.watch(boxProvider);
    final chars = ref.watch(charactersFullProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Reveal(
            child: TextButton.icon(
              onPressed: () => context.go("/teams"),
              icon: const Icon(Icons.arrow_back, size: 17),
              label: Text(l.t("back")),
            ),
          ),
          const SizedBox(height: 6),
          Reveal(
            delayMs: 40,
            child: Text(
              l.t("creatorTitle"),
              style:
                  const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 4),
          Reveal(
            delayMs: 70,
            child: Text(
              l.t("creatorSubtitle"),
              style: TextStyle(color: Colors.white.withValues(alpha: 0.6)),
            ),
          ),
          const SizedBox(height: 22),
          box.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => GlassCard(child: Text("Erreur : $e")),
            data: (playerBox) {
              if (playerBox == null) {
                return GlassCard(child: Text(l.t("teamsNoBox")));
              }
              final supported = ref.watch(gcsimSupportedProvider).maybeWhen(
                    data: (s) => s,
                    orElse: () => null,
                  );
              return chars.when(
                loading: () =>
                    const Center(child: CircularProgressIndicator()),
                error: (e, _) => GlassCard(child: Text("Erreur : $e")),
                data: (list) =>
                    _content(l, cs, playerBox, list, supported),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _content(L l, ColorScheme cs, PlayerBox playerBox,
      List<CharacterFull> list, Set<String>? supported) {
    bool isSupported(String goodKey) =>
        supported == null ||
        supported.contains(GcsimService.gcsimName(goodKey));
    final byGood = {for (final c in list) c.good: c};
    // roster possédé, montés d'abord
    final roster = playerBox.chars.values
        .where((o) => byGood.containsKey(o.key))
        .toList()
      ..sort((a, b) {
        final d = b.level.compareTo(a.level);
        return d != 0
            ? d
            : byGood[a.key]!.name.compareTo(byGood[b.key]!.name);
      });

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ---- équipes sauvegardées ----
        if (_saved.isNotEmpty) ...[
          Reveal(
            child: _Section(
              title: l.t("creatorSaved"),
              icon: Icons.bookmark,
              child: Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  for (final t in _saved)
                    InkWell(
                      borderRadius: BorderRadius.circular(13),
                      onTap: () => _loadTeam(t),
                      child: Container(
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
                              if (byGood[k] != null)
                                Padding(
                                  padding: const EdgeInsets.only(right: 4),
                                  child: CharIcon(
                                    name: byGood[k]!.name,
                                    icon: byGood[k]!.icon,
                                    element: byGood[k]!.element,
                                    size: 30,
                                    showName: false,
                                  ),
                                ),
                            const SizedBox(width: 8),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(t.name,
                                    style: const TextStyle(
                                        fontSize: 12.5,
                                        fontWeight: FontWeight.w700)),
                                Text(
                                  "${switch (t.mode) {
                                    "abyss" => l.t("modeAbyss"),
                                    "theater" => l.t("modeTheater"),
                                    _ => l.t("modeOnslaught"),
                                  }}${t.lastDps != null ? " · ${t.lastDps} DPS" : ""}",
                                  style: TextStyle(
                                      fontSize: 10.5, color: cs.primary),
                                ),
                              ],
                            ),
                            IconButton(
                              icon: const Icon(Icons.close, size: 15),
                              onPressed: () async {
                                final updated = _saved
                                    .where((x) => x.name != t.name)
                                    .toList();
                                await saveCustomTeams(updated);
                                ref.invalidate(customTeamsProvider);
                                if (mounted) {
                                  setState(() => _saved = updated);
                                }
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],

        // ---- 1. choisir 4 persos ----
        Reveal(
          delayMs: 60,
          child: _Section(
            title: "1 · ${l.t("creatorStep1")}",
            icon: Icons.people_alt,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    for (var i = 0; i < 4; i++)
                      Padding(
                        padding: const EdgeInsets.only(right: 10),
                        child: i < _picked.length &&
                                byGood[_picked[i]] != null
                            ? InkWell(
                                onTap: () => setState(() {
                                  _steps.removeWhere(
                                      (s) => s.goodKey == _picked[i]);
                                  if (_activeChar == _picked[i]) {
                                    _activeChar = null;
                                  }
                                  _picked.removeAt(i);
                                }),
                                child: CharIcon(
                                  name: byGood[_picked[i]]!.name,
                                  icon: byGood[_picked[i]]!.icon,
                                  element: byGood[_picked[i]]!.element,
                                  size: 52,
                                  showName: true,
                                ),
                              )
                            : Container(
                                width: 52,
                                height: 52,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(15),
                                  border: Border.all(
                                    color: Colors.white
                                        .withValues(alpha: 0.15),
                                    width: 1.4,
                                  ),
                                ),
                                child: Icon(Icons.add,
                                    color: Colors.white
                                        .withValues(alpha: 0.3)),
                              ),
                      ),
                  ],
                ),
                const SizedBox(height: 14),
                SizedBox(
                  width: 280,
                  child: TextField(
                    onChanged: (v) => setState(() => _search = v),
                    decoration: InputDecoration(
                      hintText: l.t("searchHint"),
                      prefixIcon: const Icon(Icons.search, size: 18),
                      filled: true,
                      fillColor: Colors.white.withValues(alpha: 0.05),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  height: 96,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    children: [
                      for (final o in roster)
                        if (_search.isEmpty ||
                            byGood[o.key]!
                                .name
                                .toLowerCase()
                                .contains(_search.toLowerCase()))
                          Padding(
                            padding: const EdgeInsets.only(right: 10),
                            child: Tooltip(
                              message: isSupported(o.key)
                                  ? byGood[o.key]!.name
                                  : l.t("simUnsupported"),
                              child: InkWell(
                                onTap: _picked.contains(o.key) ||
                                        !isSupported(o.key)
                                    ? null
                                    : () => setState(() {
                                          if (_picked.length < 4) {
                                            _picked.add(o.key);
                                            _activeChar ??= o.key;
                                          }
                                        }),
                                child: Opacity(
                                  opacity: !isSupported(o.key)
                                      ? 0.22
                                      : _picked.contains(o.key)
                                          ? 0.35
                                          : 1,
                                  child: Column(
                                    children: [
                                      CharIcon(
                                        name: byGood[o.key]!.name,
                                        icon: byGood[o.key]!.icon,
                                        element: byGood[o.key]!.element,
                                        size: 50,
                                        showName: true,
                                      ),
                                      Text(
                                        isSupported(o.key)
                                            ? "Nv ${o.level}"
                                            : "⛔",
                                        style: TextStyle(
                                          fontSize: 9.5,
                                          color: o.level >= 70
                                              ? Colors.white
                                                  .withValues(alpha: 0.45)
                                              : _amber
                                                  .withValues(alpha: 0.8),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
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

        // ---- 2. rotation ----
        if (_picked.length == 4) ...[
          Reveal(
            child: _Section(
              title: "2 · ${l.t("creatorStep2")}",
              icon: Icons.route,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // sélecteur de perso actif
                  Row(
                    children: [
                      for (final k in _picked)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: InkWell(
                            onTap: () =>
                                setState(() => _activeChar = k),
                            child: AnimatedContainer(
                              duration:
                                  const Duration(milliseconds: 180),
                              padding: const EdgeInsets.all(3),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(17),
                                border: Border.all(
                                  color: _activeChar == k
                                      ? elementColor(
                                          byGood[k]!.element)
                                      : Colors.transparent,
                                  width: 2,
                                ),
                              ),
                              child: CharIcon(
                                name: byGood[k]!.name,
                                icon: byGood[k]!.icon,
                                element: byGood[k]!.element,
                                size: 44,
                                showName: false,
                              ),
                            ),
                          ),
                        ),
                      const SizedBox(width: 12),
                      if (_activeChar != null) ...[
                        _ActionBtn(
                            label: "E",
                            tip: l.t("creatorActSkill"),
                            onTap: () => _addStep("skill")),
                        _ActionBtn(
                            label: "Q",
                            tip: l.t("creatorActBurst"),
                            onTap: () => _addStep("burst")),
                        // ATQ ×n : nombre libre (1..8) via - / +
                        Container(
                          margin: const EdgeInsets.only(right: 6),
                          decoration: BoxDecoration(
                            color: Theme.of(context)
                                .colorScheme
                                .primary
                                .withValues(alpha: 0.14),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                                color: Theme.of(context)
                                    .colorScheme
                                    .primary
                                    .withValues(alpha: 0.4)),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              InkWell(
                                onTap: () => setState(() => _atkCount =
                                    (_atkCount - 1).clamp(1, 8)),
                                child: const Padding(
                                  padding: EdgeInsets.symmetric(
                                      horizontal: 7, vertical: 8),
                                  child: Icon(Icons.remove, size: 14),
                                ),
                              ),
                              Tooltip(
                                message:
                                    "$_atkCount ${l.t("creatorActAttackN")}",
                                child: InkWell(
                                  onTap: () => _addStep("attack"),
                                  child: Padding(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 6, vertical: 9),
                                    child: Text(
                                      "ATQ ×$_atkCount",
                                      style: const TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w800),
                                    ),
                                  ),
                                ),
                              ),
                              InkWell(
                                onTap: () => setState(() => _atkCount =
                                    (_atkCount + 1).clamp(1, 8)),
                                child: const Padding(
                                  padding: EdgeInsets.symmetric(
                                      horizontal: 7, vertical: 8),
                                  child: Icon(Icons.add, size: 14),
                                ),
                              ),
                            ],
                          ),
                        ),
                        _ActionBtn(
                            label: "CHARGÉE",
                            tip: l.t("creatorActCharge"),
                            onTap: () => _addStep("charge")),
                        _ActionBtn(
                            label: "DASH",
                            tip: l.t("creatorActDash"),
                            onTap: () => _addStep("dash")),
                        _ActionBtn(
                            label: "SAUT",
                            tip: l.t("creatorActJump"),
                            onTap: () => _addStep("jump")),
                      ],
                    ],
                  ),
                  // Astuce anti-piège : un ulti en tout début de rotation
                  // démarre à 0 énergie -> la simulation attend dans le vide.
                  if (_steps.isNotEmpty && _steps.first.action == "burst") ...[
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        const Text("💡", style: TextStyle(fontSize: 13)),
                        const SizedBox(width: 7),
                        Expanded(
                          child: Text(
                            l.t("creatorTipBurstFirst"),
                            style: const TextStyle(
                                fontSize: 11.5, color: _amber, height: 1.4),
                          ),
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 14),
                  if (_steps.isEmpty)
                    Text(
                      l.t("creatorNoSteps"),
                      style: TextStyle(
                          fontSize: 12.5,
                          color: Colors.white.withValues(alpha: 0.45)),
                    )
                  else
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        for (var i = 0; i < _steps.length; i++)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 5),
                            decoration: BoxDecoration(
                              color: elementColor(
                                      byGood[_steps[i].goodKey]!.element)
                                  .withValues(alpha: 0.14),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                color: elementColor(byGood[
                                        _steps[i].goodKey]!
                                    .element)
                                    .withValues(alpha: 0.4),
                              ),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text("${i + 1}.",
                                    style: TextStyle(
                                        fontSize: 10,
                                        color: Colors.white
                                            .withValues(alpha: 0.5))),
                                const SizedBox(width: 5),
                                CharIcon(
                                  name: byGood[_steps[i].goodKey]!.name,
                                  icon: byGood[_steps[i].goodKey]!.icon,
                                  element:
                                      byGood[_steps[i].goodKey]!.element,
                                  size: 22,
                                  showName: false,
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  _actionLabel(_steps[i]),
                                  style: const TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w700),
                                ),
                                const SizedBox(width: 4),
                                InkWell(
                                  onTap: () => setState(
                                      () => _steps.removeAt(i)),
                                  child: Icon(Icons.close,
                                      size: 13,
                                      color: Colors.white
                                          .withValues(alpha: 0.6)),
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
          const SizedBox(height: 16),

          // ---- 3. simuler ----
          Reveal(
            child: _Section(
              title: "3 · ${l.t("creatorStep3")}",
              icon: Icons.speed,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // mode visé — la team sauvegardée apparaîtra dans « Équipes »
                  Row(
                    children: [
                      Text(
                        l.t("creatorModeLabel"),
                        style: TextStyle(
                            fontSize: 12.5,
                            color: Colors.white.withValues(alpha: 0.6)),
                      ),
                      const SizedBox(width: 10),
                      for (final (id, label) in [
                        ("abyss", l.t("modeAbyss")),
                        ("theater", l.t("modeTheater")),
                        ("onslaught", l.t("modeOnslaught")),
                      ])
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(label,
                                style: const TextStyle(fontSize: 12)),
                            selected: _mode == id,
                            onSelected: (_) =>
                                setState(() => _mode = id),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      SizedBox(
                        width: 240,
                        child: TextField(
                          controller: _nameCtrl,
                          decoration: InputDecoration(
                            hintText: l.t("creatorNameHint"),
                            filled: true,
                            fillColor:
                                Colors.white.withValues(alpha: 0.05),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                            contentPadding: const EdgeInsets.symmetric(
                                horizontal: 14, vertical: 10),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      FilledButton.icon(
                        onPressed: _steps.isEmpty || _running
                            ? null
                            : _simulate,
                        icon: _running
                            ? const SizedBox(
                                width: 15,
                                height: 15,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2),
                              )
                            : const Icon(Icons.speed, size: 18),
                        label: Text(_running
                            ? l.t("simRunning")
                            : l.t("simButton")),
                      ),
                      const SizedBox(width: 10),
                      IconButton(
                        tooltip: l.t("simHowTitle"),
                        icon: Icon(Icons.info_outline,
                            size: 19,
                            color: Colors.white.withValues(alpha: 0.6)),
                        onPressed: () => showSimInfoDialog(context, l),
                      ),
                    ],
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      _error!,
                      style:
                          const TextStyle(fontSize: 12, color: _amber),
                    ),
                  ],
                  if (_result != null) ...[
                    const SizedBox(height: 14),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          "${_result!.dps}",
                          style: TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.w800,
                            color: cs2(context).primary,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Padding(
                          padding: const EdgeInsets.only(bottom: 5),
                          child: Text(
                            "${l.t("simDpsLabel")} · min ${_result!.dpsMin.round()} / max ${_result!.dpsMax.round()}",
                            style: TextStyle(
                                fontSize: 12,
                                color: Colors.white
                                    .withValues(alpha: 0.6)),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    const SizedBox(height: 10),
                    SimBreakdown(result: _result!),
                    const SizedBox(height: 10),
                    OutlinedButton.icon(
                      onPressed: () => _save(l),
                      icon: const Icon(Icons.bookmark_add, size: 17),
                      label: Text(l.t("creatorSave")),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }

  static ColorScheme cs2(BuildContext c) => Theme.of(c).colorScheme;

  void _addStep(String action) {
    if (_activeChar == null) return;
    setState(() =>
        _steps.add(RotationStep(_activeChar!, action, _atkCount)));
  }

  String _actionLabel(RotationStep s) => switch (s.action) {
        "skill" => "E",
        "burst" => "Q",
        "charge" => "CHARGÉE",
        "dash" => "DASH",
        "jump" => "SAUT",
        _ => "ATQ ×${s.count}",
      };
}

/// Dialogue « comment le DPS est-il calculé ? » (partagé avec la page Équipes).
void showSimInfoDialog(BuildContext context, L l) {
  showDialog<void>(
    context: context,
    builder: (context) => AlertDialog(
      backgroundColor: const Color(0xFF15151F),
      title: Text(l.t("simHowTitle")),
      content: SizedBox(
        width: 460,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l.t("simHowBody"),
              style: const TextStyle(fontSize: 13, height: 1.6),
            ),
            const SizedBox(height: 12),
            FutureBuilder<String>(
              future: GcsimService.version(),
              builder: (context, snap) => Text(
                "${l.t("simEngineVersion")} : gcsim ${snap.data ?? "…"} "
                "(${l.t("simEngineBuiltFromSource")})",
                style: TextStyle(
                  fontSize: 11.5,
                  color: Colors.white.withValues(alpha: 0.5),
                ),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text("OK"),
        ),
      ],
    ),
  );
}

class _ActionBtn extends StatelessWidget {
  final String label;
  final String tip;
  final VoidCallback onTap;
  const _ActionBtn(
      {required this.label, required this.tip, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: Tooltip(
        message: tip,
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          onTap: onTap,
          child: Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
            decoration: BoxDecoration(
              color: cs.primary.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(10),
              border:
                  Border.all(color: cs.primary.withValues(alpha: 0.4)),
            ),
            child: Text(
              label,
              style: const TextStyle(
                  fontSize: 12, fontWeight: FontWeight.w800),
            ),
          ),
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final IconData icon;
  final Widget child;
  const _Section(
      {required this.title, required this.icon, required this.child});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 17, color: cs.primary),
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
