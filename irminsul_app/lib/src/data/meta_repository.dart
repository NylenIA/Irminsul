import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/meta_ota.dart";

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

  /// Template gcsim validé (null = pas encore de simulation pour cette équipe).
  final GcsimTemplateData? gcsim;

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
    required this.gcsim,
  });
}

/// Données brutes du template gcsim (clés GOOD + script de rotation).
class GcsimTemplateData {
  final List<String> chars;
  final String rotation;
  const GcsimTemplateData(this.chars, this.rotation);
}

/// Contenu ACTUEL d'un mode de fin de jeu (cycle en cours, stratégie).
class ModeContent {
  final String cycle;
  final String headline; // bénédiction / éléments / boss
  final String detail; // étage 12 / ouverture / (vide)
  final String strategy;
  const ModeContent(this.cycle, this.headline, this.detail, this.strategy);
}

class CurrentContent {
  final String updated;
  final Map<String, ModeContent> byMode; // abyss | theater | onslaught
  const CurrentContent(this.updated, this.byMode);
}

class MetaDb {
  final String metaVersion;
  final String lunaName; // nom officiel en jeu (ex. « Luna VIII » pour 6.7)
  final String dataKind;
  final List<MetaTeam> teams;
  final CurrentContent? content;

  /// « embedded » = livrée avec le build · « ota » = téléchargée depuis GitHub.
  final String dataSource;

  /// Clé de fraîcheur (date de contenu | version) — sert à la comparaison OTA.
  final String freshness;

  const MetaDb(this.metaVersion, this.lunaName, this.dataKind, this.teams,
      this.content, this.dataSource, this.freshness);

  /// Libellé complet de version, côté jeu ET côté données.
  String get versionLabel =>
      lunaName.isEmpty ? metaVersion : "$metaVersion · $lunaName";

  List<MetaTeam> byMode(String mode) =>
      teams.where((t) => t.mode == mode).toList();
}

/// Charge la BDD méta : celle téléchargée (OTA) si elle est plus fraîche que
/// celle embarquée dans le build, sinon l'asset. Un build plus récent gagne
/// toujours sur un vieux cache — la comparaison porte sur la date de contenu.
final metaDbProvider = FutureProvider<MetaDb>((ref) async {
  final raw = await rootBundle.loadString("assets/data/meta_teams.json");
  var json = jsonDecode(raw) as Map<String, dynamic>;
  var source = "embedded";
  final ota = await MetaOta.cached();
  if (ota != null &&
      MetaOta.freshness(ota).compareTo(MetaOta.freshness(json)) > 0) {
    json = ota;
    source = "ota";
  }
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
      gcsim: m["gcsim"] == null
          ? null
          : GcsimTemplateData(
              ((m["gcsim"] as Map)["chars"] as List).cast<String>(),
              (m["gcsim"] as Map)["rotation"] as String,
            ),
    );
  }).toList();
  CurrentContent? content;
  final rawContent = json["content"] as Map<String, dynamic>?;
  if (rawContent != null) {
    ModeContent parseMode(String key, String h, String d) {
      final m = rawContent[key] as Map<String, dynamic>? ?? const {};
      return ModeContent(
        m["cycle"] as String? ?? "",
        m[h] as String? ?? "",
        m[d] as String? ?? "",
        m["strategy"] as String? ?? "",
      );
    }

    content = CurrentContent(
      rawContent["updated"] as String? ?? "",
      {
        "abyss": parseMode("abyss", "blessing", "floor12"),
        "theater": parseMode("theater", "elements", "opening"),
        "onslaught": parseMode("onslaught", "bosses", ""),
      },
    );
  }

  return MetaDb(
    json["metaVersion"] as String,
    json["lunaName"] as String? ?? "",
    json["dataKind"] as String? ?? "DEMO",
    teams,
    content,
    source,
    MetaOta.freshness(json),
  );
});
