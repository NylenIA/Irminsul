import "characters_repository.dart";
import "meta_repository.dart";
import "../services/box_service.dart";

/// Résultat d'un slot d'équipe après croisement avec la box.
class SlotMatch {
  final TeamSlot slot;
  final CharacterFull character; // perso retenu (titulaire ou alternative)
  final bool owned;
  final bool viaAlt;
  final OwnedChar? ownedData;
  final double? erValue; // % ER calculée (artefacts + arme, depuis le GOOD)
  final bool erWarning;
  final CharacterFull? suggestion; // remplaçant possédé « en attendant »
  final OwnedChar? suggestionData;

  const SlotMatch({
    required this.slot,
    required this.character,
    required this.owned,
    required this.viaAlt,
    required this.ownedData,
    required this.erValue,
    required this.erWarning,
    required this.suggestion,
    required this.suggestionData,
  });

  /// Perso possédé mais clairement pas monté (à builder avant de compter dessus).
  bool get lowLevel => owned && (ownedData?.level ?? 90) < 70;
}

/// Une équipe méta croisée avec la box du joueur.
class TeamMatch {
  final MetaTeam team;
  final List<SlotMatch> slots;

  const TeamMatch({required this.team, required this.slots});

  int get ownedCount => slots.where((s) => s.owned).length;
  bool get complete => ownedCount == slots.length;
  List<SlotMatch> get missing => slots.where((s) => !s.owned).toList();
  bool get hasErWarning => slots.any((s) => s.erWarning);
}

/// Croise la BDD méta avec la box. Règle produit : on ne bricole JAMAIS —
/// un slot non possédé (ni titulaire ni alternative) reste « manquant ».
List<TeamMatch> matchTeams({
  required MetaDb meta,
  required PlayerBox box,
  required List<CharacterFull> characters,
}) {
  final byId = {for (final c in characters) c.id: c};

  TeamMatch buildMatch(MetaTeam team) {
    final slots = <SlotMatch>[];
    for (final slot in team.slots) {
      CharacterFull? chosen = byId[slot.id];
      OwnedChar? ownedData;
      var viaAlt = false;

      // titulaire possédé ?
      if (chosen != null) {
        ownedData = box.chars[chosen.good];
      }
      // sinon, une alternative possédée ?
      if (ownedData == null) {
        for (final altId in slot.alts) {
          final alt = byId[altId];
          final altOwned = alt == null ? null : box.chars[alt.good];
          if (altOwned != null) {
            chosen = alt;
            ownedData = altOwned;
            viaAlt = true;
            break;
          }
        }
      }
      if (chosen == null) continue; // id inconnu dans la BDD : ignore

      final owned = ownedData != null;
      double? erVal;
      var erWarn = false;
      final req = slot.er;
      if (owned && req != null && req > 0) {
        erVal = box.erByChar[chosen.good];
        // ER réelle (artefacts + arme) : petite tolérance d'arrondi.
        erWarn = erVal != null && erVal + 3 < req;
      }

      // slot manquant → meilleur remplaçant POSSÉDÉ du pool (« en attendant »)
      CharacterFull? suggestion;
      OwnedChar? suggestionData;
      if (!owned) {
        for (final pid in slot.pool) {
          final cand = byId[pid];
          final candOwned = cand == null ? null : box.chars[cand.good];
          if (candOwned != null) {
            suggestion = cand;
            suggestionData = candOwned;
            break;
          }
        }
      }

      slots.add(SlotMatch(
        slot: slot,
        character: chosen,
        owned: owned,
        viaAlt: viaAlt,
        ownedData: ownedData,
        erValue: erVal,
        erWarning: erWarn,
        suggestion: suggestion,
        suggestionData: suggestionData,
      ));
    }
    return TeamMatch(team: team, slots: slots);
  }

  final matches = meta.teams.where((t) => t.slots.isNotEmpty).map(buildMatch).toList()
    ..sort((a, b) {
      // complètes d'abord, puis par nombre de manquants croissant
      final d = (b.complete ? 1 : 0) - (a.complete ? 1 : 0);
      if (d != 0) return d;
      return a.missing.length.compareTo(b.missing.length);
    });
  return matches;
}
