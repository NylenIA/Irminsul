import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/box_service.dart";
import "characters_repository.dart";
import "meta_repository.dart";

/// Ce que sait faire un personnage (généré par tool/gen_character_tags.py
/// depuis les descriptions officielles FR, avec corrections explicites).
class CharTags {
  final String element;
  final int rarity;
  final List<String> tags; // heal, shield, atk_buff, res_shred, offfield…
  final bool carry; // peut porter une équipe
  final List<String> reactions; // réactions rendues possibles par l'élément

  const CharTags({
    required this.element,
    required this.rarity,
    required this.tags,
    required this.carry,
    required this.reactions,
  });

  bool has(String t) => tags.contains(t);
}

final charTagsProvider = FutureProvider<Map<String, CharTags>>((ref) async {
  final raw = await rootBundle.loadString("assets/data/character_tags.json");
  final j = jsonDecode(raw) as Map<String, dynamic>;
  return j.map((k, v) {
    final m = v as Map<String, dynamic>;
    return MapEntry(
      k,
      CharTags(
        element: m["element"] as String? ?? "",
        rarity: (m["rarity"] as num?)?.toInt() ?? 4,
        tags: (m["tags"] as List? ?? const []).cast<String>(),
        carry: m["carry"] as bool? ?? false,
        reactions: (m["reactions"] as List? ?? const []).cast<String>(),
      ),
    );
  });
});

/// Une ligne du calcul, affichée telle quelle dans l'app : le joueur doit
/// pouvoir vérifier POURQUOI une équipe est proposée.
class ScoreLine {
  final String label;
  final double factor; // multiplicateur appliqué (1.0 = neutre)
  final String kind; // "content" | "box" | "team"
  const ScoreLine(this.label, this.factor, this.kind);
}

/// Une équipe proposée par le moteur, avec son score détaillé.
class BuiltTeam {
  final List<CharacterFull> chars;
  final CharacterFull carry;
  final double score;
  final double basePower; // puissance brute avant contenu/box
  final List<ScoreLine> lines;

  /// Persos à monter pour que l'équipe soit vraiment jouable (Nv/artefacts).
  final List<String> toBuild;

  /// Persos non possédés (variante « si tu l'obtiens »).
  final List<String> missing;

  const BuiltTeam({
    required this.chars,
    required this.carry,
    required this.score,
    required this.basePower,
    required this.lines,
    required this.toBuild,
    required this.missing,
  });

  bool get playableNow => missing.isEmpty && toBuild.isEmpty;
  String get id => (chars.map((c) => c.id).toList()..sort()).join("+");
}

/// Contraintes et bonus du contenu en cours, lus depuis meta_teams.json.
class ContentRules {
  /// Éléments autorisés (Théâtre) — vide = pas de restriction.
  final List<String> allowedElements;
  final List<String> guests;

  /// Réactions amplifiées par le cycle → bonus (0.75 = +75 %).
  final Map<String, double> boostedReactions;

  /// Éléments dont l'absence coûte cher (mécanique de salle/boss).
  final List<String> requiredElements;

  /// Rôles favorisés (ex. bouclier/soin contre un boss unique).
  final List<String> favoredTags;

  const ContentRules({
    this.allowedElements = const [],
    this.guests = const [],
    this.boostedReactions = const {},
    this.requiredElements = const [],
    this.favoredTags = const [],
  });

  static ContentRules from(ModeContent? c) {
    if (c == null) return const ContentRules();
    return ContentRules(
      allowedElements: c.allowedElements,
      guests: c.guests,
      boostedReactions: c.boostedReactions,
      requiredElements: c.requiredElements,
      favoredTags: c.favoredTags,
    );
  }
}

/// Réactions réalisables par un ensemble d'éléments présents dans l'équipe.
const _reactionPairs = <String, List<String>>{
  "vaporize": ["pyro", "hydro"],
  "melt": ["pyro", "cryo"],
  "overloaded": ["pyro", "electro"],
  "superconduct": ["cryo", "electro"],
  "electro-charged": ["hydro", "electro"],
  "frozen": ["hydro", "cryo"],
  "bloom": ["hydro", "dendro"],
  "hyperbloom": ["hydro", "dendro", "electro"],
  "burgeon": ["hydro", "dendro", "pyro"],
  "burning": ["pyro", "dendro"],
  "aggravate": ["dendro", "electro"],
  "quicken": ["dendro", "electro"],
  "spread": ["dendro", "electro"],
  "swirl": ["anemo"],
  "crystallize": ["geo"],
  // réactions lunaires : mêmes paires, activées par les unités « Lune »
  "lunar-charged": ["hydro", "electro"],
  "lunar-bloom": ["hydro", "dendro"],
  "stellar-conduct": ["cryo", "electro"],
};

bool _canTrigger(String reaction, Set<String> elements) {
  final need = _reactionPairs[reaction];
  if (need == null) return false;
  return need.every(elements.contains);
}

/// Qualité de montage d'un perso, 0 → 1. Un Nv 1 sans artefacts ne peut pas
/// être proposé comme s'il valait un Nv 90 équipé : c'est ce facteur qui
/// empêche l'app de conseiller l'injouable.
double buildQuality(OwnedChar? c, BuildInfo? b) {
  if (c == null) return 0;
  final lvl = (c.level / 90).clamp(0.15, 1.0);
  final talents =
      ((c.talentSkill + c.talentBurst) / 18).clamp(0.15, 1.0).toDouble();
  final art = b == null || b.artifactCount == 0
      ? 0.35
      : (0.55 + 0.09 * b.artifactCount).clamp(0.55, 1.0).toDouble();
  final weapon = b == null || b.weaponLevel <= 20
      ? 0.55
      : (0.6 + 0.4 * (b.weaponLevel / 90)).clamp(0.6, 1.0).toDouble();
  return lvl * 0.35 + talents * 0.25 + art * 0.25 + weapon * 0.15;
}

/// Poids des rôles de support : ce que chaque étiquette apporte à l'équipe.
/// Rendements décroissants : un 2ᵉ buff d'ATQ vaut moins que le premier.
const _tagValue = <String, double>{
  "atk_buff": 0.26,
  "dmg_buff": 0.24,
  "res_shred": 0.22,
  "em_buff": 0.14,
  "heal": 0.12,
  "shield": 0.12,
  "offfield": 0.16,
  "energy": 0.10,
  "crowd": 0.06,
  "interrupt": 0.05,
  "nightsoul": 0.04,
};

/// Construit et classe des équipes DEPUIS LA BOX pour un contenu donné.
/// Déterministe et explicable : aucune magie, chaque facteur est affiché.
class TeamBuilder {
  final Map<String, CharacterFull> byGood;
  final Map<String, CharTags> tags;
  final PlayerBox box;
  final ContentRules rules;

  /// true = on propose aussi des équipes avec des persos non possédés ou pas
  /// montés (variante « si tu montes / si tu l'obtiens »).
  final bool includeAspirational;

  TeamBuilder({
    required this.byGood,
    required this.tags,
    required this.box,
    required this.rules,
    this.includeAspirational = true,
  });

  bool _elementAllowed(CharacterFull c) =>
      rules.allowedElements.isEmpty ||
      rules.allowedElements.contains(c.element.toLowerCase()) ||
      rules.guests.any((g) => g.toLowerCase() == c.name.toLowerCase());

  double _supportValue(CharacterFull c, Map<String, int> seen) {
    final t = tags[c.good];
    if (t == null) return 0;
    var v = 0.0;
    for (final tag in t.tags) {
      final w = _tagValue[tag];
      if (w == null) continue;
      final n = seen[tag] ?? 0;
      v += w / (1 + n); // 2ᵉ occurrence : moitié moins utile
      seen[tag] = n + 1;
    }
    return v;
  }

  /// Score de contenu : c'est ICI que « l'équipe colle au contenu » se décide.
  (double, List<ScoreLine>) _contentScore(List<CharacterFull> team) {
    final lines = <ScoreLine>[];
    final elements = team.map((c) => c.element.toLowerCase()).toSet();
    var mult = 1.0;

    // Réactions amplifiées par le cycle.
    // On ne cumule PAS toutes les réactions possibles : une équipe ne
    // déclenche vraiment que celle qu'elle applique en boucle. On prend donc
    // la MEILLEURE réaction réellement soutenue (le porteur en fait partie,
    // ou un applicateur hors terrain la nourrit), + une petite prime si une
    // seconde est jouable en secours.
    final carryElement = team.first.element.toLowerCase();
    final appliers = <String>{
      for (final c in team)
        if ((tags[c.good]?.has("offfield") ?? false) ||
            (tags[c.good]?.carry ?? false))
          c.element.toLowerCase(),
    };
    var best = 0.0;
    var bestName = "";
    var second = 0.0;
    rules.boostedReactions.forEach((reaction, boost) {
      if (!_canTrigger(reaction, elements)) return;
      final need = _reactionPairs[reaction]!;
      // le porteur participe à la réaction → plein effet
      // sinon il faut au moins que les deux éléments soient appliqués
      final carried = need.contains(carryElement);
      final fed = need.every(appliers.contains);
      if (!carried && !fed) return;
      final f = 1 + boost * (carried ? 0.30 : 0.15);
      if (f > best) {
        second = best;
        best = f;
        bestName = reaction;
      } else if (f > second) {
        second = f;
      }
    });
    if (best > 0) {
      mult *= best;
      lines.add(ScoreLine("$bestName amplifié ce cycle", best, "content"));
      if (second > 0) {
        mult *= 1.05;
        lines.add(const ScoreLine(
            "seconde réaction boostée jouable", 1.05, "content"));
      }
    } else if (rules.boostedReactions.isNotEmpty) {
      mult *= 0.80;
      lines.add(const ScoreLine(
          "ne profite d'aucune réaction amplifiée du cycle", 0.80, "content"));
    }

    // éléments imposés par une mécanique (salle, boss)
    for (final e in rules.requiredElements) {
      if (!elements.contains(e)) {
        mult *= 0.45;
        lines.add(ScoreLine("il manque du $e exigé par le contenu", 0.45,
            "content"));
      }
    }

    // rôles favorisés (bouclier/soin sur boss unique…)
    for (final tag in rules.favoredTags) {
      if (team.any((c) => tags[c.good]?.has(tag) ?? false)) {
        mult *= 1.08;
        lines.add(ScoreLine("$tag utile sur ce contenu", 1.08, "content"));
      }
    }
    return (mult, lines);
  }

  List<BuiltTeam> build({int limit = 6}) {
    final owned = box.chars;
    final pool = byGood.values.where(_elementAllowed).toList();

    // --- carries candidats : possédés d'abord, triés par montage ----------
    final carries = pool
        .where((c) => tags[c.good]?.carry ?? false)
        .map((c) => (
              c,
              buildQuality(owned[c.good], box.buildByChar[c.good]),
              owned.containsKey(c.good)
            ))
        .toList()
      ..sort((a, b) {
        if (a.$3 != b.$3) return a.$3 ? -1 : 1;
        return b.$2.compareTo(a.$2);
      });

    // --- supports candidats : les plus utiles d'abord ---------------------
    final supports = pool
        .where((c) => !(tags[c.good]?.carry ?? false) || !owned.containsKey(c.good))
        .map((c) {
          final q = buildQuality(owned[c.good], box.buildByChar[c.good]);
          final t = tags[c.good];
          final util = t == null
              ? 0.0
              : t.tags
                  .map((x) => _tagValue[x] ?? 0)
                  .fold<double>(0, (a, b) => a + b);
          return (c, util * (owned.containsKey(c.good) ? (0.4 + q) : 0.35));
        })
        .toList()
      ..sort((a, b) => b.$2.compareTo(a.$2));

    final shortSupports =
        supports.take(includeAspirational ? 18 : 14).map((e) => e.$1).toList();

    final out = <String, BuiltTeam>{};
    for (final (carry, cq, carryOwned) in carries.take(8)) {
      if (!carryOwned && !includeAspirational) continue;
      final cand = shortSupports.where((s) => s.id != carry.id).toList();
      for (var i = 0; i < cand.length; i++) {
        for (var j = i + 1; j < cand.length; j++) {
          for (var k = j + 1; k < cand.length; k++) {
            final team = [carry, cand[i], cand[j], cand[k]];
            final built = _score(team, carry, cq);
            if (built == null) continue;
            final prev = out[built.id];
            if (prev == null || built.score > prev.score) out[built.id] = built;
          }
        }
      }
    }

    final list = out.values.toList()
      ..sort((a, b) {
        // jouable maintenant d'abord, à score comparable (−15 % de marge)
        if (a.playableNow != b.playableNow) {
          final better = a.playableNow ? a : b;
          final other = a.playableNow ? b : a;
          if (better.score >= other.score * 0.85) {
            return a.playableNow ? -1 : 1;
          }
        }
        return b.score.compareTo(a.score);
      });
    return list.take(limit).toList();
  }

  BuiltTeam? _score(
      List<CharacterFull> team, CharacterFull carry, double carryQuality) {
    final owned = box.chars;
    final missing = <String>[];
    final toBuild = <String>[];
    final lines = <ScoreLine>[];

    var boxFactor = 1.0;
    for (final c in team) {
      final oc = owned[c.good];
      if (oc == null) {
        missing.add(c.name);
        boxFactor *= 0.55;
        continue;
      }
      final q = buildQuality(oc, box.buildByChar[c.good]);
      if (oc.level < 70 || (box.buildByChar[c.good]?.artifactCount ?? 0) < 5) {
        toBuild.add(c.name);
      }
      boxFactor *= (0.55 + 0.45 * q);
    }
    if (missing.isNotEmpty && !includeAspirational) return null;

    // recharge d'énergie : un support qui ne peut pas lancer son ultime
    // n'apporte pas son buff — on le paye dans le score.
    var erPenalty = 1.0;
    for (final c in team) {
      final er = box.erByChar[c.good];
      final t = tags[c.good];
      if (er != null && t != null && !t.carry && er < 140) {
        erPenalty *= 0.94;
      }
    }
    if (erPenalty < 1) {
      lines.add(ScoreLine("recharge d'énergie juste sur un support",
          erPenalty, "box"));
    }

    // puissance d'équipe : porteur + apports des supports
    final seen = <String, int>{};
    var support = 0.0;
    for (final c in team) {
      if (c.id == carry.id) continue;
      support += _supportValue(c, seen);
    }
    final rarityBonus = carry.rarity >= 5 ? 1.12 : 1.0;
    final base = (0.55 + carryQuality) * rarityBonus * (1 + support);

    final (contentMult, contentLines) = _contentScore(team);
    lines.addAll(contentLines);
    lines.add(ScoreLine("montage réel de tes persos", boxFactor, "box"));
    lines.add(ScoreLine("apport des supports", 1 + support, "team"));

    return BuiltTeam(
      chars: team,
      carry: carry,
      score: base * contentMult * boxFactor * erPenalty,
      basePower: base,
      lines: lines,
      toBuild: toBuild,
      missing: missing,
    );
  }
}
