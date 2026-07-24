import "dart:convert";
import "dart:io";

import "box_service.dart";

/// Résultat d'une simulation gcsim.
class SimResult {
  final int dps;
  final double dpsMin;
  final double dpsMax;
  final int iterations;
  const SimResult({
    required this.dps,
    required this.dpsMin,
    required this.dpsMax,
    required this.iterations,
  });
}

class GcsimException implements Exception {
  final String message;
  const GcsimException(this.message);
  @override
  String toString() => message;
}

/// Template de rotation gcsim d'une équipe (validé hors-ligne avant embarquement).
class GcsimTemplate {
  final List<String> chars; // clés GOOD, ordre = ordre du script
  final String rotation;
  const GcsimTemplate(this.chars, this.rotation);
}

/// Pont gcsim : génère une config depuis le GOOD sauvegardé (stats RÉELLES du
/// joueur : niveaux, constellations, talents, arme, artefacts) et lance le
/// binaire embarqué. Étiquette produit : « rotation standard simplifiée ».
class GcsimService {
  static const _iterations = 100;

  static const _charMap = {
    "RaidenShogun": "raiden",
    "KaedeharaKazuha": "kazuha",
    "KamisatoAyaka": "ayaka",
    "KamisatoAyato": "ayato",
    "SangonomiyaKokomi": "kokomi",
    "KukiShinobu": "kuki",
    "YaeMiko": "yaemiko",
    "AratakiItto": "itto",
    "KujouSara": "sara",
    "ShikanoinHeizou": "heizou",
    "HuTao": "hutao",
  };

  static const _ascMax = [20, 40, 50, 60, 70, 80, 90];

  // stat GOOD -> (clé gcsim, est un pourcentage)
  static const _statMap = <String, (String, bool)>{
    "hp": ("hp", false), "hp_": ("hp%", true),
    "atk": ("atk", false), "atk_": ("atk%", true),
    "def": ("def", false), "def_": ("def%", true),
    "eleMas": ("em", false), "enerRech_": ("er", true),
    "critRate_": ("cr", true), "critDMG_": ("cd", true),
    "heal_": ("heal", true), "physical_dmg_": ("phys%", true),
    "pyro_dmg_": ("pyro%", true), "hydro_dmg_": ("hydro%", true),
    "cryo_dmg_": ("cryo%", true), "electro_dmg_": ("electro%", true),
    "anemo_dmg_": ("anemo%", true), "geo_dmg_": ("geo%", true),
    "dendro_dmg_": ("dendro%", true),
  };

  static const _mainMax5 = <String, double>{
    "hp": 4780, "atk": 311.5, "hp_": 46.6, "atk_": 46.6, "def_": 58.3,
    "eleMas": 186.5, "enerRech_": 51.8, "critRate_": 31.1, "critDMG_": 62.2,
    "heal_": 35.9, "physical_dmg_": 58.3, "pyro_dmg_": 46.6,
    "hydro_dmg_": 46.6, "cryo_dmg_": 46.6, "electro_dmg_": 46.6,
    "anemo_dmg_": 46.6, "geo_dmg_": 46.6, "dendro_dmg_": 46.6,
  };
  static const _mainMax4 = <String, double>{
    "hp": 3571, "atk": 232, "hp_": 34.8, "atk_": 34.8, "def_": 43.5,
    "eleMas": 139.3, "enerRech_": 38.7, "critRate_": 23.3, "critDMG_": 46.6,
    "heal_": 26.8, "physical_dmg_": 43.5, "pyro_dmg_": 34.8,
    "hydro_dmg_": 34.8, "cryo_dmg_": 34.8, "electro_dmg_": 34.8,
    "anemo_dmg_": 34.8, "geo_dmg_": 34.8, "dendro_dmg_": 34.8,
  };

  /// Chemin du binaire embarqué (à côté de l'exécutable de l'app).
  static File binary() {
    final dir = File(Platform.resolvedExecutable).parent.path;
    return File("$dir${Platform.pathSeparator}gcsim.exe");
  }

  static Future<bool> available() => binary().exists();

  static double? _mainValue(String key, int rarity, int level) {
    final table = rarity >= 5 ? _mainMax5 : _mainMax4;
    final mx = table[key];
    if (mx == null) return null;
    final maxLvl = rarity >= 5 ? 20 : 16;
    final lvl = level.clamp(0, maxLvl);
    return mx * (0.15 + 0.85 * lvl / maxLvl);
  }

  static String _g(String goodKey) =>
      _charMap[goodKey] ?? goodKey.toLowerCase();

  /// Nom gcsim public d'une clé GOOD (pour le créateur de rotations).
  static String gcsimName(String goodKey) => _g(goodKey);

  /// Construit la config gcsim complète depuis le GOOD brut.
  static String buildConfig(
      Map<String, dynamic> good, GcsimTemplate template) {
    final chars = <String, Map<String, dynamic>>{
      for (final c in good["characters"] as List? ?? const [])
        if (c is Map<String, dynamic> && c["key"] is String)
          c["key"] as String: c,
    };
    final buf = StringBuffer();
    for (final gk in template.chars) {
      final c = chars[gk];
      if (c == null) {
        throw GcsimException("Personnage absent de ta box : $gk");
      }
      final name = _g(gk);
      final asc = ((c["ascension"] as num?)?.toInt() ?? 6).clamp(0, 6);
      final t = c["talent"] as Map? ?? const {};
      buf.writeln(
          "$name char lvl=${c["level"] ?? 90}/${_ascMax[asc]} "
          "cons=${c["constellation"] ?? 0} "
          "talent=${t["auto"] ?? 6},${t["skill"] ?? 6},${t["burst"] ?? 6};");

      Map<String, dynamic>? weapon;
      for (final w in good["weapons"] as List? ?? const []) {
        if (w is Map<String, dynamic> && w["location"] == gk) {
          weapon = w;
          break;
        }
      }
      if (weapon == null) {
        throw GcsimException("Aucune arme équipée sur $gk");
      }
      final wAsc = ((weapon["ascension"] as num?)?.toInt() ?? 6).clamp(0, 6);
      buf.writeln(
          '$name add weapon="${(weapon["key"] as String).toLowerCase()}" '
          "refine=${weapon["refinement"] ?? 1} "
          "lvl=${weapon["level"] ?? 90}/${_ascMax[wAsc]};");

      final setCounts = <String, int>{};
      final totals = <String, double>{};
      for (final a in good["artifacts"] as List? ?? const []) {
        if (a is! Map || a["location"] != gk) continue;
        final setKey = a["setKey"] as String? ?? "";
        if (setKey.isNotEmpty) {
          setCounts[setKey] = (setCounts[setKey] ?? 0) + 1;
        }
        final mv = _mainValue(
          a["mainStatKey"] as String? ?? "",
          (a["rarity"] as num?)?.toInt() ?? 5,
          (a["level"] as num?)?.toInt() ?? 0,
        );
        if (mv != null) {
          final k = a["mainStatKey"] as String;
          totals[k] = (totals[k] ?? 0) + mv;
        }
        for (final s in a["substats"] as List? ?? const []) {
          if (s is! Map) continue;
          final k = s["key"] as String? ?? "";
          final v = (s["value"] as num?)?.toDouble() ?? 0;
          if (k.isNotEmpty) totals[k] = (totals[k] ?? 0) + v;
        }
      }
      final sets = setCounts.entries.where((e) => e.value >= 2).toList()
        ..sort((a, b) => a.key.compareTo(b.key));
      for (final e in sets) {
        buf.writeln('$name add set="${e.key.toLowerCase()}" '
            "count=${e.value >= 4 ? 4 : 2};");
      }
      final parts = <String>[];
      final keys = totals.keys.toList()..sort();
      for (final k in keys) {
        final m = _statMap[k];
        if (m == null) continue;
        final (gKey, pct) = m;
        parts.add(pct
            ? "$gKey=${(totals[k]! / 100).toStringAsFixed(4)}"
            : "$gKey=${totals[k]!.toStringAsFixed(1)}");
      }
      if (parts.isNotEmpty) {
        buf.writeln("$name add stats ${parts.join(" ")};");
      }
      buf.writeln();
    }
    buf.writeln("active ${_g(template.chars.first)};");
    buf.writeln(
        "options iteration=$_iterations duration=90 swap_delay=12;");
    buf.writeln("target lvl=100 resist=0.1;");
    buf.writeln("energy every interval=480,720 amount=1;");
    buf.writeln();
    buf.writeln(template.rotation);
    return buf.toString();
  }

  /// Lance la simulation sur la box sauvegardée. ~5-30 s selon la machine.
  static Future<SimResult> run(GcsimTemplate template) async {
    final bin = binary();
    if (!await bin.exists()) {
      throw const GcsimException(
          "Moteur gcsim introuvable à côté de l'application.");
    }
    final raw = await BoxService.readSavedRaw();
    if (raw == null) {
      throw const GcsimException("Aucune box importée.");
    }
    final good = jsonDecode(raw) as Map<String, dynamic>;
    final config = buildConfig(good, template);

    final tmp = await Directory.systemTemp.createTemp("irminsul_gcsim");
    try {
      final cfg = File("${tmp.path}${Platform.pathSeparator}config.txt");
      await cfg.writeAsString(config);
      final proc = await Process.run(
        bin.path,
        ["-c", cfg.path],
        stdoutEncoding: utf8,
        stderrEncoding: utf8,
      ).timeout(const Duration(minutes: 3));
      final out = "${proc.stdout}\n${proc.stderr}";
      final m = RegExp(
              r"resulting in (\d+) dps \(min: ([\d.]+) max: ([\d.]+)")
          .firstMatch(out);
      if (m == null) {
        final err = out.trim();
        throw GcsimException(
            "Simulation échouée : ${err.isEmpty ? "sortie vide" : err.substring(0, err.length.clamp(0, 220))}");
      }
      return SimResult(
        dps: int.parse(m.group(1)!),
        dpsMin: double.parse(m.group(2)!),
        dpsMax: double.parse(m.group(3)!),
        iterations: _iterations,
      );
    } finally {
      await tmp.delete(recursive: true);
    }
  }
}
