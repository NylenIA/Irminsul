import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

class WeaponRec {
  final String name;
  final String note;
  const WeaponRec(this.name, this.note);
}

class ArtifactRec {
  final String set;
  final String sands;
  final String goblet;
  final String circlet;
  final String subs;
  const ArtifactRec(this.set, this.sands, this.goblet, this.circlet, this.subs);
}

class ConstellationNote {
  final String c;
  final String text;
  const ConstellationNote(this.c, this.text);
}

class Materials {
  final String gems;
  final String boss;
  final String local;
  final String common;
  final String talent;
  final String weekly;
  const Materials(this.gems, this.boss, this.local, this.common, this.talent,
      this.weekly);
}

class CharacterSheet {
  final String id;
  final String name;
  final String icon;
  final String element;
  final int rarity;
  final String weaponType;
  final String role;
  final String pitch;
  final List<String> talents;
  final List<WeaponRec> weapons;
  final ArtifactRec artifacts;
  final List<ConstellationNote> constellations;
  final Materials materials;

  const CharacterSheet({
    required this.id,
    required this.name,
    required this.icon,
    required this.element,
    required this.rarity,
    required this.weaponType,
    required this.role,
    required this.pitch,
    required this.talents,
    required this.weapons,
    required this.artifacts,
    required this.constellations,
    required this.materials,
  });
}

/// Charge les fiches persos embarquées (assets/data/characters.json).
final charactersProvider = FutureProvider<List<CharacterSheet>>((ref) async {
  final raw = await rootBundle.loadString("assets/data/characters.json");
  final json = jsonDecode(raw) as Map<String, dynamic>;
  return (json["characters"] as List).map((c) {
    final m = c as Map<String, dynamic>;
    final a = m["artifacts"] as Map<String, dynamic>;
    final mat = m["materials"] as Map<String, dynamic>;
    return CharacterSheet(
      id: m["id"] as String,
      name: m["name"] as String,
      icon: m["icon"] as String,
      element: m["element"] as String,
      rarity: m["rarity"] as int,
      weaponType: m["weaponType"] as String,
      role: m["role"] as String,
      pitch: m["pitch"] as String,
      talents: (m["talents"] as List).cast<String>(),
      weapons: (m["weapons"] as List)
          .map((w) => WeaponRec(w["n"] as String, w["r"] as String))
          .toList(),
      artifacts: ArtifactRec(
        a["set"] as String,
        a["sands"] as String,
        a["goblet"] as String,
        a["circlet"] as String,
        a["subs"] as String,
      ),
      constellations: (m["constellations"] as List)
          .map((k) => ConstellationNote(k["c"] as String, k["t"] as String))
          .toList(),
      materials: Materials(
        mat["gems"] as String,
        mat["boss"] as String,
        mat["local"] as String,
        mat["common"] as String,
        mat["talent"] as String,
        mat["weekly"] as String,
      ),
    );
  }).toList();
});
