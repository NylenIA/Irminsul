import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

/// Un personnage d'une équipe méta.
class TeamChar {
  final String name;
  final String element;
  final String icon;
  const TeamChar(this.name, this.element, this.icon);
}

/// Ce qui manque au joueur pour débloquer la team.
class MissingInfo {
  final String character;
  final String gain;
  const MissingInfo(this.character, this.gain);
}

/// Un slot d'équipe : titulaire + alternatives acceptées + exigence d'ER
/// + pool de remplaçants « en attendant » (classés du meilleur au moins bon).
class TeamSlot {
  final String id; // id de perso (characters_full)
  final List<String> alts;
  final int? er; // % de recharge conseillé (null/0 = pas d'exigence)
  final String role;
  final List<String> pool;
  const TeamSlot(this.id, this.alts, this.er, this.role, this.pool);
}

/// Une équipe méta (démo pour l'instant — BDD curée + gcsim ensuite).
class MetaTeam {
  final String id;
  final String mode; // abyss | theater | onslaught
  final String name;
  final String half;
  final String badge; // meta | viable | locked
  final int dps;
  final String rotation;
  final String note;
  final List<TeamChar> chars;
  final MissingInfo? missing;
  final List<TeamSlot> slots;
  final List<String> rotationSteps;
  final String combos;

  const MetaTeam({
    required this.id,
    required this.mode,
    required this.name,
    required this.half,
    required this.badge,
    required this.dps,
    required this.rotation,
    required this.note,
    required this.chars,
    required this.missing,
    required this.slots,
    required this.rotationSteps,
    required this.combos,
  });
}

class MetaDb {
  final String metaVersion;
  final String dataKind;
  final List<MetaTeam> teams;
  const MetaDb(this.metaVersion, this.dataKind, this.teams);

  List<MetaTeam> byMode(String mode) =>
      teams.where((t) => t.mode == mode).toList();
}

/// Charge la BDD méta embarquée (assets/data/meta_teams.json).
final metaDbProvider = FutureProvider<MetaDb>((ref) async {
  final raw = await rootBundle.loadString("assets/data/meta_teams.json");
  final json = jsonDecode(raw) as Map<String, dynamic>;
  final teams = (json["teams"] as List).map((t) {
    final m = t as Map<String, dynamic>;
    return MetaTeam(
      id: m["id"] as String,
      mode: m["mode"] as String,
      name: m["name"] as String,
      half: m["half"] as String? ?? "",
      badge: m["badge"] as String,
      dps: m["dps"] as int,
      rotation: m["rotation"] as String? ?? "",
      note: m["note"] as String? ?? "",
      chars: (m["chars"] as List)
          .map((c) => TeamChar(
              c["n"] as String, c["e"] as String, c["i"] as String? ?? ""))
          .toList(),
      missing: m["missing"] == null
          ? null
          : MissingInfo(
              (m["missing"] as Map)["char"] as String,
              (m["missing"] as Map)["gain"] as String,
            ),
      slots: (m["slots"] as List? ?? const [])
          .map((s) => TeamSlot(
                s["id"] as String,
                (s["alts"] as List? ?? const []).cast<String>(),
                (s["er"] as num?)?.toInt(),
                s["role"] as String? ?? "",
                (s["pool"] as List? ?? const []).cast<String>(),
              ))
          .toList(),
      rotationSteps:
          (m["rotationSteps"] as List? ?? const []).cast<String>(),
      combos: m["combos"] as String? ?? "",
    );
  }).toList();
  return MetaDb(
    json["metaVersion"] as String,
    json["dataKind"] as String? ?? "DEMO",
    teams,
  );
});
