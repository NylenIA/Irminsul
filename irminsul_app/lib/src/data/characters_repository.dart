import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

// ---------------------------------------------------------------------------
// Base COMPLÈTE (120 persos) — générée depuis genshin-db (données du jeu, FR)
// par tool/gen_characters_db.py. Zéro donnée inventée.
// ---------------------------------------------------------------------------

class TalentInfo {
  final String slot;
  final String name;
  final String icon;
  final String desc;
  const TalentInfo(this.slot, this.name, this.icon, this.desc);
}

class ConstellationInfo {
  final int n;
  final String name;
  final String icon;
  final String desc;
  const ConstellationInfo(this.n, this.name, this.icon, this.desc);
}

class MatEntry {
  final String name;
  final int qty;
  final String icon;
  const MatEntry(this.name, this.qty, this.icon);
}

/// Archons jouables (+ Furina, archonne de fait pendant Fontaine).
const archonIds = {
  "venti", "zhongli", "raidenshogun", "nahida", "furina", "mavuika",
};

class CharacterFull {
  final String id;
  final String name;
  final String title;
  final String element;
  final int rarity;
  final String weaponType;
  final String region;
  final String description;
  final String icon; // nom d'asset complet (UI_AvatarIcon_…)
  final String splash; // splash art gacha (UI_Gacha_AvatarImg_…)
  final List<TalentInfo> talents;
  final List<ConstellationInfo> cons;
  final List<MatEntry> matAscension;
  final List<MatEntry> matTalents;

  bool get isArchon => archonIds.contains(id);

  const CharacterFull({
    required this.id,
    required this.name,
    required this.title,
    required this.element,
    required this.rarity,
    required this.weaponType,
    required this.region,
    required this.description,
    required this.icon,
    required this.splash,
    required this.talents,
    required this.cons,
    required this.matAscension,
    required this.matTalents,
  });
}

final charactersFullProvider =
    FutureProvider<List<CharacterFull>>((ref) async {
  final raw =
      await rootBundle.loadString("assets/data/characters_full.json");
  final json = jsonDecode(raw) as Map<String, dynamic>;
  return (json["characters"] as List).map((c) {
    final m = c as Map<String, dynamic>;
    return CharacterFull(
      id: m["id"] as String,
      name: m["name"] as String,
      title: m["title"] as String? ?? "",
      element: m["element"] as String,
      rarity: m["rarity"] as int,
      weaponType: m["weaponType"] as String? ?? "",
      region: m["region"] as String? ?? "",
      description: m["description"] as String? ?? "",
      icon: m["icon"] as String,
      splash: m["splash"] as String? ?? "",
      talents: (m["talents"] as List)
          .map((t) => TalentInfo(
                t["slot"] as String,
                t["name"] as String,
                t["icon"] as String? ?? "",
                t["desc"] as String? ?? "",
              ))
          .toList(),
      cons: (m["cons"] as List)
          .map((k) => ConstellationInfo(
                k["n"] as int,
                k["name"] as String,
                k["icon"] as String? ?? "",
                k["desc"] as String? ?? "",
              ))
          .toList(),
      matAscension: (m["matAscension"] as List)
          .map((x) => MatEntry(
              x["n"] as String, x["q"] as int, x["i"] as String? ?? ""))
          .toList(),
      matTalents: (m["matTalents"] as List)
          .map((x) => MatEntry(
              x["n"] as String, x["q"] as int, x["i"] as String? ?? ""))
          .toList(),
    );
  }).toList();
});

// ---------------------------------------------------------------------------
// LEAKS — contenu NON confirmé, toujours étiqueté (docs/LEAK_POLICY).
// ---------------------------------------------------------------------------

class LeakKitPart {
  final String title;
  final String desc;
  const LeakKitPart(this.title, this.desc);
}

class LeakSource {
  final String name;
  final String date;
  const LeakSource(this.name, this.date);
}

class LeakCharacter {
  final String id;
  final String name;
  final String element;
  final int rarity;
  final String weaponType;
  final String expected;
  final String kitVersion;
  final int score;
  final String grade;
  final String summary;
  final List<LeakKitPart> kit;
  final List<LeakSource> sources;

  const LeakCharacter({
    required this.id,
    required this.name,
    required this.element,
    required this.rarity,
    required this.weaponType,
    required this.expected,
    required this.kitVersion,
    required this.score,
    required this.grade,
    required this.summary,
    required this.kit,
    required this.sources,
  });
}

class LeaksDb {
  final String disclaimer;
  final String updated;
  final List<LeakCharacter> characters;
  const LeaksDb(this.disclaimer, this.updated, this.characters);
}

final leaksProvider = FutureProvider<LeaksDb>((ref) async {
  final raw = await rootBundle.loadString("assets/data/leaks.json");
  final json = jsonDecode(raw) as Map<String, dynamic>;
  return LeaksDb(
    json["disclaimer"] as String,
    json["updated"] as String,
    (json["characters"] as List).map((c) {
      final m = c as Map<String, dynamic>;
      return LeakCharacter(
        id: m["id"] as String,
        name: m["name"] as String,
        element: m["element"] as String,
        rarity: m["rarity"] as int,
        weaponType: m["weaponType"] as String,
        expected: m["expected"] as String,
        kitVersion: m["kitVersion"] as String,
        score: m["score"] as int,
        grade: m["grade"] as String,
        summary: m["summary"] as String,
        kit: (m["kit"] as List)
            .map((k) => LeakKitPart(k["t"] as String, k["d"] as String))
            .toList(),
        sources: (m["sources"] as List)
            .map((s) => LeakSource(s["n"] as String, s["d"] as String))
            .toList(),
      );
    }).toList(),
  );
});

// ---------------------------------------------------------------------------
// Builds CURÉS (standards communautaires, étiquetés) — characters.json.
// Séparés des données du jeu ; étendus patch après patch via la synchro.
// ---------------------------------------------------------------------------

class WeaponRec {
  final String name; // nom FR (vérifié dans les données du jeu)
  final String note;
  final String icon;
  const WeaponRec(this.name, this.note, this.icon);
}

class ArtifactRec {
  final String setName; // nom FR
  final String setIcon;
  final String sands;
  final String goblet;
  final String circlet;
  final String subs;
  const ArtifactRec(this.setName, this.setIcon, this.sands, this.goblet,
      this.circlet, this.subs);
}

class ConstellationNote {
  final String c;
  final String text;
  const ConstellationNote(this.c, this.text);
}

class CuratedBuild {
  final String id;
  final String role;
  final String pitch;
  final List<String> talentPriority;
  final List<WeaponRec> weapons;
  final ArtifactRec artifacts;
  final List<ConstellationNote> constellations;

  const CuratedBuild({
    required this.id,
    required this.role,
    required this.pitch,
    required this.talentPriority,
    required this.weapons,
    required this.artifacts,
    required this.constellations,
  });
}

final curatedBuildsProvider =
    FutureProvider<Map<String, CuratedBuild>>((ref) async {
  final raw = await rootBundle.loadString("assets/data/characters.json");
  final json = jsonDecode(raw) as Map<String, dynamic>;
  final map = <String, CuratedBuild>{};
  for (final c in json["characters"] as List) {
    final m = c as Map<String, dynamic>;
    final a = m["artifacts"] as Map<String, dynamic>;
    map[m["id"] as String] = CuratedBuild(
      id: m["id"] as String,
      role: m["role"] as String,
      pitch: m["pitch"] as String,
      talentPriority: (m["talents"] as List).cast<String>(),
      weapons: (m["weapons"] as List)
          .map((w) => WeaponRec(
                w["fr"] as String? ?? w["n"] as String,
                w["r"] as String,
                w["icon"] as String? ?? "",
              ))
          .toList(),
      artifacts: ArtifactRec(
        a["setfr"] as String? ?? a["set"] as String,
        a["seticon"] as String? ?? "",
        a["sands"] as String,
        a["goblet"] as String,
        a["circlet"] as String,
        a["subs"] as String,
      ),
      constellations: (m["constellations"] as List)
          .map((k) => ConstellationNote(k["c"] as String, k["t"] as String))
          .toList(),
    );
  }
  return map;
});
