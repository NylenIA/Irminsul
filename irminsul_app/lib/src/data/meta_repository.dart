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

/// Une équipe méta curée (rotation gcsim validée par simulation).
class MetaTeam {
  final String id;

  /// Mode principal (compat) — voir [modes] pour tous les modes où l'équipe
  /// est recommandée (une même équipe peut servir en Abîme ET au Théâtre).
  final String mode; // abyss | theater | onslaught
  final List<String> modes;
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

  /// L'équipe est-elle proposée pour ce mode ?
  bool servesMode(String m) => modes.contains(m);

  const MetaTeam({
    required this.id,
    required this.mode,
    required this.modes,
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

  /// Bornes du cycle (ISO, vides si inconnues) : l'app en déduit « en cours »,
  /// « commence dans X j » ou « terminé » plutôt que de croire une phrase figée.
  final String from;
  final String to;

  /// Restriction d'éléments (Théâtre) : vide = aucune restriction.
  final List<String> allowedElements;

  /// Invités autorisés hors restriction d'éléments (Théâtre).
  final List<String> guests;

  /// D'où vient l'info + date de vérification (affiché tel quel).
  final String source;

  const ModeContent(
    this.cycle,
    this.headline,
    this.detail,
    this.strategy, {
    this.from = "",
    this.to = "",
    this.allowedElements = const [],
    this.guests = const [],
    this.source = "",
  });

  DateTime? get startsAt => DateTime.tryParse(from);
  DateTime? get endsAt => DateTime.tryParse(to);

  /// État du cycle par rapport à une date donnée : -1 à venir, 0 en cours,
  /// 1 terminé, null si les bornes sont inconnues.
  int? statusAt(DateTime now) {
    final s = startsAt;
    final e = endsAt;
    if (s == null && e == null) return null;
    if (s != null && now.isBefore(s)) return -1;
    // la borne de fin est inclusive (le cycle court jusqu'à la fin du jour)
    if (e != null && now.isAfter(e.add(const Duration(days: 1)))) return 1;
    return 0;
  }

  /// Jours restants (ou avant le début si le cycle n'a pas commencé).
  int? daysLeftAt(DateTime now) {
    final st = statusAt(now);
    if (st == null || st == 1) return null;
    final target = st == -1 ? startsAt : endsAt;
    if (target == null) return null;
    return target.add(const Duration(days: 1)).difference(now).inDays;
  }

  /// Un personnage de cet élément est-il jouable dans ce contenu ?
  bool allowsElement(String element) =>
      allowedElements.isEmpty ||
      allowedElements.contains(element.toLowerCase());

  bool isGuest(String name) =>
      guests.any((g) => g.toLowerCase() == name.toLowerCase());
}

class CurrentContent {
  final String updated;
  final Map<String, ModeContent> byMode; // abyss | theater | onslaught
  const CurrentContent(this.updated, this.byMode);
}

/// Filtre les équipes selon la restriction du contenu en cours (Théâtre).
/// Une équipe dont un personnage n'est ni d'un élément autorisé ni invité
/// est INJOUABLE ce mois-ci : on ne la propose pas plutôt que de mentir.
List<T> filterBySeason<T>(
  List<T> items,
  ModeContent? content,
  List<TeamChar> Function(T) charsOf,
) {
  if (content == null || content.allowedElements.isEmpty) return items;
  return items
      .where((it) => charsOf(it).every((c) =>
          content.allowsElement(c.element) || content.isGuest(c.name)))
      .toList();
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
      teams.where((t) => t.servesMode(mode)).toList();
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
      modes: (m["modes"] as List? ?? [m["mode"]]).cast<String>(),
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
        from: m["from"] as String? ?? "",
        to: m["to"] as String? ?? "",
        allowedElements:
            (m["allowedElements"] as List? ?? const []).cast<String>(),
        guests: (m["guests"] as List? ?? const []).cast<String>(),
        source: m["source"] as String? ?? "",
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
