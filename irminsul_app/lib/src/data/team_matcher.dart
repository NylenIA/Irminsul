import "characters_repository.dart";
import "meta_repository.dart";
import "../services/box_service.dart";

/// Seuil « perso réellement montable en équipe ». En dessous, on le signale
/// (« à monter ») plutôt que de le proposer comme s'il était prêt.
const kBuiltLevel = 70;

/// Un candidat possédé pour un slot.
class _Cand {
  final CharacterFull character;
  final OwnedChar owned;
  final int rank; // priorité méta (ordre dans alts/pool)
  const _Cand(this.character, this.owned, this.rank);

  bool get built => owned.level >= kBuiltLevel;
}

/// Trie les candidats : les persos RÉELLEMENT montés d'abord (par priorité
/// méta), puis les non montés du plus haut niveau au plus bas.
/// Évite de conseiller « Layla Nv 1 » quand « Diona Nv 80 » est disponible.
void _sortCandidates(List<_Cand> list) {
  list.sort((a, b) {
    if (a.built != b.built) return a.built ? -1 : 1;
    if (a.built) return a.rank.compareTo(b.rank);
    final byLevel = b.owned.level.compareTo(a.owned.level);
    return byLevel != 0 ? byLevel : a.rank.compareTo(b.rank);
  });
}

/// Résultat d'un slot d'équipe après croisement avec la box.
class SlotMatch {
  final TeamSlot slot;
  final CharacterFull character; // perso retenu (titulaire ou alternative)
  final bool owned;
  final bool viaAlt;
  final OwnedChar? ownedData;
  final BuildInfo? buildInfo;
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
    required this.buildInfo,
    required this.erValue,
    required this.erWarning,
    required this.suggestion,
    required this.suggestionData,
  });

  /// Possédé mais pas monté : à builder avant de compter dessus.
  bool get lowLevel => owned && (ownedData?.level ?? 99) < kBuiltLevel;

  /// Aucun artefact équipé — le vrai problème, pas l'ER.
  bool get noArtifacts => owned && (buildInfo?.noArtifacts ?? false);

  /// Perso monté mais arme laissée au niveau de départ.
  bool get weakWeapon =>
      owned && !lowLevel && (buildInfo?.weakWeapon ?? false);

  /// Le remplaçant proposé est-il lui-même à monter ?
  bool get suggestionNeedsBuild =>
      suggestionData != null && suggestionData!.level < kBuiltLevel;
}

/// Une équipe méta croisée avec la box du joueur.
class TeamMatch {
  final MetaTeam team;
  final List<SlotMatch> slots;

  const TeamMatch({required this.team, required this.slots});

  int get ownedCount => slots.where((s) => s.owned).length;
  bool get complete => slots.isNotEmpty && ownedCount == slots.length;
  List<SlotMatch> get missing => slots.where((s) => !s.owned).toList();

  /// Complète ET tout le monde est réellement monté : jouable tout de suite.
  bool get ready => complete && slots.every((s) => !s.lowLevel);

  List<SlotMatch> get erWarnings =>
      slots.where((s) => s.erWarning).toList();
  List<SlotMatch> get equipmentWarnings =>
      slots.where((s) => s.noArtifacts || s.weakWeapon).toList();

  /// Nombre total de points d'attention (sert au classement).
  int get issueCount => erWarnings.length + equipmentWarnings.length;
}

/// Croise la BDD méta avec la box. Règle produit : on ne bricole JAMAIS —
/// un slot non pourvu (ni titulaire ni alternative) reste « manquant », et on
/// propose au mieux un remplaçant possédé, en disant s'il est à monter.
List<TeamMatch> matchTeams({
  required MetaDb meta,
  required PlayerBox box,
  required List<CharacterFull> characters,
}) {
  final byId = {for (final c in characters) c.id: c};

  _Cand? bestOf(List<String> ids) {
    final cands = <_Cand>[];
    for (var i = 0; i < ids.length; i++) {
      final c = byId[ids[i]];
      final o = c == null ? null : box.chars[c.good];
      if (c != null && o != null) cands.add(_Cand(c, o, i));
    }
    if (cands.isEmpty) return null;
    _sortCandidates(cands);
    return cands.first;
  }

  TeamMatch buildMatch(MetaTeam team) {
    final slots = <SlotMatch>[];
    for (final slot in team.slots) {
      final titular = byId[slot.id];
      if (titular == null) continue; // id inconnu : on ignore le slot

      var chosen = titular;
      var ownedData = box.chars[titular.good];
      var viaAlt = false;

      // Titulaire absent → meilleure alternative POSSÉDÉE (montée d'abord).
      if (ownedData == null) {
        final alt = bestOf(slot.alts);
        if (alt != null) {
          chosen = alt.character;
          ownedData = alt.owned;
          viaAlt = true;
        }
      }

      final owned = ownedData != null;
      final build = owned ? box.buildByChar[chosen.good] : null;

      double? erVal;
      var erWarn = false;
      final req = slot.er;
      if (owned && req != null && req > 0) {
        erVal = box.erByChar[chosen.good];
        // Pas d'alerte ER si le perso n'a aucun artefact : le message
        // « équipement » est plus juste et évite un double avertissement.
        final hasArtifacts = !(build?.noArtifacts ?? false);
        erWarn = hasArtifacts && erVal != null && erVal + 3 < req;
      }

      // Slot manquant → meilleur remplaçant possédé du pool.
      final sug = owned ? null : bestOf(slot.pool);

      slots.add(SlotMatch(
        slot: slot,
        character: chosen,
        owned: owned,
        viaAlt: viaAlt,
        ownedData: ownedData,
        buildInfo: build,
        erValue: erVal,
        erWarning: erWarn,
        suggestion: sug?.character,
        suggestionData: sug?.owned,
      ));
    }
    return TeamMatch(team: team, slots: slots);
  }

  final matches =
      meta.teams.where((t) => t.slots.isNotEmpty).map(buildMatch).toList()
        ..sort((a, b) {
          // 1) jouables tout de suite, 2) complètes, 3) moins de manquants,
          // 4) moins d'avertissements (ER/équipement), 5) DPS décroissant.
          final byReady = (b.ready ? 1 : 0) - (a.ready ? 1 : 0);
          if (byReady != 0) return byReady;
          final byComplete = (b.complete ? 1 : 0) - (a.complete ? 1 : 0);
          if (byComplete != 0) return byComplete;
          final byMissing = a.missing.length.compareTo(b.missing.length);
          if (byMissing != 0) return byMissing;
          final byIssues = a.issueCount.compareTo(b.issueCount);
          if (byIssues != 0) return byIssues;
          return b.team.dps.compareTo(a.team.dps);
        });
  return matches;
}
