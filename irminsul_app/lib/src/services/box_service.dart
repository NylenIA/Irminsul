import "dart:convert";
import "dart:io";

import "package:path_provider/path_provider.dart";

/// Un personnage possédé (fichier GOOD : Inventory Kamera / Genshin Optimizer).
class OwnedChar {
  final String key; // clé GOOD (ex. RaidenShogun)
  final int level;
  final int constellation;
  final int talentAuto;
  final int talentSkill;
  final int talentBurst;

  const OwnedChar({
    required this.key,
    required this.level,
    required this.constellation,
    required this.talentAuto,
    required this.talentSkill,
    required this.talentBurst,
  });
}

/// La box du joueur, parsée depuis un fichier GOOD.
class PlayerBox {
  final Map<String, OwnedChar> chars; // par clé GOOD

  /// Estimation de recharge d'énergie PAR PERSO, %, artefacts uniquement
  /// (base 100 + main stat sablier ER + toutes les sous-stats ER équipées).
  /// L'arme n'est pas comptée — l'étiquette UI le précise.
  final Map<String, double> erByChar;

  final String label;

  const PlayerBox({
    required this.chars,
    required this.erByChar,
    required this.label,
  });

  int get count => chars.length;
}

class BoxService {
  static const _fileName = "account.good.json";
  static const _metaName = "account.meta.json";

  /// Parse un JSON GOOD. Lève [FormatException] si invalide.
  static PlayerBox parse(String jsonStr, {String label = ""}) {
    final dynamic data = jsonDecode(jsonStr);
    if (data is! Map || data["characters"] is! List) {
      throw const FormatException(
          "Fichier invalide : pas un export GOOD (clé 'characters' absente).");
    }

    final chars = <String, OwnedChar>{};
    for (final c in data["characters"] as List) {
      if (c is! Map) continue;
      final key = c["key"] as String?;
      if (key == null || key.isEmpty) continue;
      final talent = c["talent"];
      chars[key] = OwnedChar(
        key: key,
        level: (c["level"] as num?)?.toInt() ?? 1,
        constellation: (c["constellation"] as num?)?.toInt() ?? 0,
        talentAuto: talent is Map ? (talent["auto"] as num?)?.toInt() ?? 1 : 1,
        talentSkill:
            talent is Map ? (talent["skill"] as num?)?.toInt() ?? 1 : 1,
        talentBurst:
            talent is Map ? (talent["burst"] as num?)?.toInt() ?? 1 : 1,
      );
    }

    // ---- estimation ER par perso (artefacts équipés) ----
    final er = <String, double>{};
    for (final k in chars.keys) {
      er[k] = 100.0;
    }
    if (data["artifacts"] is List) {
      for (final a in data["artifacts"] as List) {
        if (a is! Map) continue;
        final loc = a["location"] as String? ?? "";
        if (loc.isEmpty || !er.containsKey(loc)) continue;
        // main stat sablier ER (valeur approx. selon rareté/niveau)
        if (a["mainStatKey"] == "enerRech_") {
          final rarity = (a["rarity"] as num?)?.toInt() ?? 5;
          final level = (a["level"] as num?)?.toInt() ?? 0;
          final max = rarity >= 5 ? 51.8 : 38.9; // niv 20 / 16
          final maxLvl = rarity >= 5 ? 20 : 16;
          er[loc] = er[loc]! + max * (level.clamp(0, maxLvl) / maxLvl);
        }
        for (final s in (a["substats"] as List? ?? const [])) {
          if (s is Map && s["key"] == "enerRech_") {
            er[loc] = er[loc]! + ((s["value"] as num?)?.toDouble() ?? 0);
          }
        }
      }
    }

    return PlayerBox(chars: chars, erByChar: er, label: label);
  }

  static Future<File> _file(String name) async {
    final dir = await getApplicationSupportDirectory();
    return File("${dir.path}/$name");
  }

  /// Sauvegarde le GOOD brut + méta (label), en local uniquement.
  static Future<void> save(String jsonStr, String label) async {
    final f = await _file(_fileName);
    await f.create(recursive: true);
    await f.writeAsString(jsonStr);
    final m = await _file(_metaName);
    await m.writeAsString(jsonEncode({"label": label}));
  }

  /// Recharge la box sauvegardée (null si aucune).
  static Future<PlayerBox?> loadSaved() async {
    try {
      final f = await _file(_fileName);
      if (!await f.exists()) return null;
      var label = "";
      final m = await _file(_metaName);
      if (await m.exists()) {
        final meta = jsonDecode(await m.readAsString());
        if (meta is Map) label = meta["label"] as String? ?? "";
      }
      return parse(await f.readAsString(), label: label);
    } catch (_) {
      return null;
    }
  }
}
