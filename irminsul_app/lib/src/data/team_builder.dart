import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/box_service.dart";
import "../services/gcsim_service.dart";
import "characters_repository.dart";
import "meta_repository.dart";

/// Ce que sait faire un personnage (généré par tool/gen_character_tags.py
/// depuis les descriptions officielles FR, avec corrections explicites).
class CharTags {
  final String element;
  final int rarity;
  final List<String> tags; // heal, shield, atk_buff, res_shred, offfield…
  final bool carry;

  const CharTags({
    required this.element,
    required this.rarity,
    required this.tags,
    required this.carry,
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
      ),
    );
  });
});

/// Un poste d'un archétype : ce qu'il faut y mettre, et les choix reconnus.
class ArchSlot {
  final String role;
  final List<String> elements; // vide = libre
  final List<String> tags; // au moins un de ces rôles
  final List<String> prefer; // titulaires puis alternatives reconnues
  final List<String> actions; // pour générer la rotation gcsim
  final bool carry;

  const ArchSlot({
    required this.role,
    required this.elements,
    required this.tags,
    required this.prefer,
    required this.actions,
    required this.carry,
  });
}

/// Un ARCHÉTYPE d'équipe réel (Hyperbloom, Vaporisation, Lunar-Charged…).
/// C'est ce qui empêche le moteur d'inventer des combinaisons : on remplit
/// des postes définis, on n'assemble pas des persos au hasard.
class Archetype {
  final String id;
  final String name;
  final String reaction;
  final List<String> gate; // sans eux, la réaction n'existe pas
  final List<String> requiredElements;
  final double procs; // cadence estimée de la réaction transformative
  final String note;
  final List<ArchSlot> slots;

  const Archetype({
    required this.id,
    required this.name,
    required this.reaction,
    required this.gate,
    required this.requiredElements,
    required this.procs,
    required this.note,
    required this.slots,
  });
}

final archetypesProvider = FutureProvider<List<Archetype>>((ref) async {
  final raw = await rootBundle.loadString("assets/data/team_archetypes.json");
  final list = jsonDecode(raw) as List;
  return list.map((e) {
    final m = e as Map<String, dynamic>;
    return Archetype(
      id: m["id"] as String,
      name: m["name"] as String,
      reaction: m["reaction"] as String? ?? "",
      gate: (m["gate"] as List? ?? const []).cast<String>(),
      requiredElements:
          (m["requiredElements"] as List? ?? const []).cast<String>(),
      procs: (m["procs"] as num?)?.toDouble() ?? 0,
      note: m["note"] as String? ?? "",
      slots: (m["slots"] as List).map((s) {
        final sm = s as Map<String, dynamic>;
        return ArchSlot(
          role: sm["role"] as String,
          elements: (sm["elements"] as List? ?? const []).cast<String>(),
          tags: (sm["tags"] as List? ?? const []).cast<String>(),
          prefer: (sm["prefer"] as List? ?? const []).cast<String>(),
          actions: (sm["actions"] as List? ?? const ["skill"]).cast<String>(),
          carry: sm["carry"] as bool? ?? false,
        );
      }).toList(),
    );
  }).toList();
});

/// Une ligne du calcul, affichée telle quelle : le joueur doit pouvoir
/// vérifier POURQUOI une équipe est proposée.
class ScoreLine {
  final String label;
  final double factor;
  const ScoreLine(this.label, this.factor);
}

/// Un poste pourvu.
class FilledSlot {
  final ArchSlot slot;
  final CharacterFull character;
  final String why; // titulaire · alternative reconnue · meilleur de ta box
  final bool owned;
  const FilledSlot(this.slot, this.character, this.why, this.owned);
}

/// Une équipe proposée : un archétype réel, rempli avec TA box.
class BuiltTeam {
  final Archetype archetype;
  final List<FilledSlot> filled;
  final double score;
  final List<ScoreLine> lines;
  final List<String> toBuild;
  final List<String> missing;

  const BuiltTeam({
    required this.archetype,
    required this.filled,
    required this.score,
    required this.lines,
    required this.toBuild,
    required this.missing,
  });

  List<CharacterFull> get chars => filled.map((f) => f.character).toList();
  bool get playableNow => missing.isEmpty && toBuild.isEmpty;
  String get id => "${archetype.id}:${chars.map((c) => c.id).join("+")}";

  /// Rotation gcsim jouable à la main : supports d'abord, porteur ensuite.
  GcsimTemplateData get template {
    final buf = StringBuffer("while 1 {\n");
    final ordered = [...filled]..sort((a, b) {
        final ac = a.slot.carry ? 1 : 0;
        final bc = b.slot.carry ? 1 : 0;
        return ac.compareTo(bc);
      });
    for (final f in ordered) {
      final n = GcsimService.gcsimName(f.character.good);
      for (final a in f.slot.actions) {
        buf.writeln("    $n $a;");
      }
    }
    buf.write("}");
    return GcsimTemplateData(
        filled.map((f) => f.character.good).toList(), buf.toString());
  }
}

/// Contraintes et bonus du contenu en cours, lus depuis meta_teams.json.
class ContentRules {
  final List<String> allowedElements;
  final List<String> guests;
  final Map<String, double> boostedReactions;
  final List<String> requiredElements;
  final List<String> favoredTags;

  const ContentRules({
    this.allowedElements = const [],
    this.guests = const [],
    this.boostedReactions = const {},
    this.requiredElements = const [],
    this.favoredTags = const [],
  });

  static ContentRules from(ModeContent? c) => c == null
      ? const ContentRules()
      : ContentRules(
          allowedElements: c.allowedElements,
          guests: c.guests,
          boostedReactions: c.boostedReactions,
          requiredElements: c.requiredElements,
          favoredTags: c.favoredTags,
        );
}

/// Multiplicateurs de base des réactions transformatives (KQM/TCL).
const _transformative = <String, double>{
  "superconduct": 1.5,
  "electro-charged": 2.0,
  "lunar-charged": 2.0,
  "lunar-bloom": 2.0,
  "hyperbloom": 3.0,
  "burgeon": 3.0,
  "overloaded": 2.75,
  "bloom": 2.0,
  "swirl": 0.6,
};
const _levelMultiplier = 1446.85; // niveau 90
const _baselineDps = 22000.0; // référence pour convertir des DGT en facteur

double _reactionDamage(String reaction, double em, double bonus) {
  final base = _transformative[reaction];
  if (base == null) return 0;
  final emBonus = 16 * em / (em + 2000);
  return base * _levelMultiplier * (1 + emBonus + bonus) * 0.9;
}

/// Qualité de montage d'un perso, 0 → 1 : un Nv 1 sans artefacts ne peut pas
/// être proposé comme s'il valait un Nv 90 équipé.
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

/// Construit des équipes RÉELLES à partir de ta box : on part d'archétypes
/// reconnus et on pourvoit chaque poste avec le meilleur perso que tu as.
class TeamBuilder {
  final Map<String, CharacterFull> byGood;
  final Map<String, CharTags> tags;
  final List<Archetype> archetypes;
  final PlayerBox box;
  final ContentRules rules;

  /// true = proposer aussi la version « si tu obtiens / si tu montes ».
  final bool includeAspirational;

  TeamBuilder({
    required this.byGood,
    required this.tags,
    required this.archetypes,
    required this.box,
    required this.rules,
    this.includeAspirational = true,
  });

  bool _allowedByContent(String good) {
    if (rules.allowedElements.isEmpty) return true;
    final t = tags[good];
    final c = byGood[good];
    if (t == null || c == null) return false;
    return rules.allowedElements.contains(t.element) ||
        rules.guests.any((g) => g.toLowerCase() == c.name.toLowerCase());
  }

  bool _fits(String good, ArchSlot slot, Set<String> used) {
    if (used.contains(good)) return false;
    final t = tags[good];
    if (t == null || byGood[good] == null) return false;
    if (!_allowedByContent(good)) return false;
    if (slot.elements.isNotEmpty && !slot.elements.contains(t.element)) {
      return false;
    }
    if (slot.tags.isNotEmpty && !slot.tags.any(t.has)) return false;
    return true;
  }

  /// Pourvoit chaque poste : titulaire reconnu > alternative reconnue >
  /// meilleur de la box > (si autorisé) perso non possédé.
  List<FilledSlot>? _fill(Archetype a, {required bool aspirational}) {
    final used = <String>{};
    final out = <FilledSlot>[];
    for (final slot in a.slots) {
      String? pick;
      var why = "";
      for (var i = 0; i < slot.prefer.length; i++) {
        final k = slot.prefer[i];
        if (box.chars.containsKey(k) && _fits(k, slot, used)) {
          pick = k;
          why = i == 0 ? "titulaire" : "alternative reconnue";
          break;
        }
      }
      if (pick == null) {
        final cands = box.chars.keys.where((k) => _fits(k, slot, used)).toList()
          ..sort((x, y) => buildQuality(box.chars[y], box.buildByChar[y])
              .compareTo(buildQuality(box.chars[x], box.buildByChar[x])));
        if (cands.isNotEmpty) {
          pick = cands.first;
          why = "meilleur de ta box";
        }
      }
      if (pick == null && aspirational) {
        for (final k in slot.prefer) {
          if (_fits(k, slot, used)) {
            pick = k;
            why = "à obtenir";
            break;
          }
        }
      }
      if (pick == null) return null; // poste impossible → pas de bricolage
      used.add(pick);
      out.add(FilledSlot(
          slot, byGood[pick]!, why, box.chars.containsKey(pick)));
    }
    return out;
  }

  BuiltTeam? _score(Archetype a, List<FilledSlot> filled) {
    final keys = filled.map((f) => f.character.good).toSet();
    // condition de réaction (ex. Lunar-Charged sans Moonsign = impossible)
    if (a.gate.isNotEmpty && !a.gate.any(keys.contains)) return null;

    final lines = <ScoreLine>[];
    var mult = 1.0;
    final elements = filled.map((f) => f.character.element.toLowerCase()).toSet();

    final boost = rules.boostedReactions[a.reaction];
    if (boost != null && a.procs > 0) {
      final added = _reactionDamage(a.reaction, 200, boost) * a.procs;
      final f = 1 + added / _baselineDps;
      mult *= f;
      lines.add(ScoreLine(
          "${a.reaction} amplifié (≈ +${added.round()} DGT/s)", f));
    } else if (boost != null) {
      mult *= 1.15;
      lines.add(ScoreLine("${a.reaction} favorisé par le cycle", 1.15));
    } else if (rules.boostedReactions.isNotEmpty) {
      mult *= 0.92;
      lines.add(const ScoreLine("hors réactions amplifiées du cycle", 0.92));
    }

    for (final e in rules.requiredElements) {
      if (!elements.contains(e)) {
        mult *= 0.5;
        lines.add(ScoreLine("pas de $e exigé par le contenu", 0.5));
      }
    }
    for (final tg in rules.favoredTags) {
      if (filled.any((f) => tags[f.character.good]?.has(tg) ?? false)) {
        mult *= 1.06;
        lines.add(ScoreLine("$tg utile sur ce contenu", 1.06));
      }
    }

    var boxFactor = 1.0;
    final missing = <String>[];
    final toBuild = <String>[];
    for (final f in filled) {
      final good = f.character.good;
      final oc = box.chars[good];
      if (oc == null) {
        missing.add(f.character.name);
        boxFactor *= 0.5;
        continue;
      }
      final q = buildQuality(oc, box.buildByChar[good]);
      if (oc.level < 70 || (box.buildByChar[good]?.artifactCount ?? 0) < 5) {
        toBuild.add(f.character.name);
      }
      boxFactor *= 0.55 + 0.45 * q;
    }
    lines.add(ScoreLine("montage réel de ta box", boxFactor));

    return BuiltTeam(
      archetype: a,
      filled: filled,
      score: mult * boxFactor,
      lines: lines,
      toBuild: toBuild,
      missing: missing,
    );
  }

  List<BuiltTeam> build({int limit = 5}) {
    final out = <BuiltTeam>[];
    for (final a in archetypes) {
      var team = _fill(a, aspirational: false);
      var built = team == null ? null : _score(a, team);
      if (built == null && includeAspirational) {
        team = _fill(a, aspirational: true);
        built = team == null ? null : _score(a, team);
      }
      if (built != null) out.add(built);
    }
    out.sort((x, y) {
      if (x.missing.isEmpty != y.missing.isEmpty) {
        return x.missing.isEmpty ? -1 : 1;
      }
      return y.score.compareTo(x.score);
    });
    return out.take(limit).toList();
  }
}
