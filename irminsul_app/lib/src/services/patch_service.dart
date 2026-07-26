import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../data/meta_repository.dart";
import "meta_ota.dart";

/// État de synchronisation des données méta (principe OTA : le code est séparé
/// des données ; la référence vit sur GitHub et l'app compare au démarrage).
enum SyncState { upToDate, updateAvailable, offline }

class SyncStatus {
  final SyncState state;
  final String localVersion;
  final String? remoteVersion;

  /// Date du contenu de cycle côté distant (ex. « 2026-07-25 »), utile quand
  /// la version du jeu ne change pas mais que l'Abîme, lui, tourne.
  final String? remoteUpdated;

  /// « embedded » ou « ota » : d'où viennent les données actuellement lues.
  final String source;

  /// Pourquoi la synchro ne marche pas : « network » (pas de réseau) ou
  /// « unreachable » (la source répond mais refuse : dépôt privé, 404…).
  final String? reason;

  const SyncStatus(
    this.state,
    this.localVersion,
    this.remoteVersion, {
    this.remoteUpdated,
    this.source = "embedded",
    this.reason,
  });
}

final syncStatusProvider = FutureProvider<SyncStatus>((ref) async {
  final local = await ref.watch(metaDbProvider.future);
  final res = await MetaOta.fetch();
  final remote = res.json;
  if (remote == null) {
    return SyncStatus(
      SyncState.offline,
      local.metaVersion,
      null,
      source: local.dataSource,
      reason: res.status == 0 ? "network" : "unreachable",
    );
  }
  final remoteVersion = remote["metaVersion"] as String;
  final remoteContent = remote["content"] as Map<String, dynamic>?;
  final newer =
      MetaOta.freshness(remote).compareTo(local.freshness) > 0;
  return SyncStatus(
    newer ? SyncState.updateAvailable : SyncState.upToDate,
    local.metaVersion,
    remoteVersion,
    remoteUpdated: remoteContent?["updated"] as String?,
    source: local.dataSource,
  );
});

/// Mise à jour AUTOMATIQUE au démarrage (même principe que le moteur gcsim,
/// qui est recompilé chaque jour) : si la méta distante est plus fraîche que
/// tout ce qu'on a en local, on l'installe et on recharge — sans réinstaller
/// l'app, et sans rien casser si le réseau est absent.
/// Ne dépend PAS de metaDbProvider : pas de boucle d'invalidation.
final metaAutoSyncProvider = FutureProvider<bool>((ref) async {
  final asset = jsonDecode(
      await rootBundle.loadString("assets/data/meta_teams.json"))
      as Map<String, dynamic>;
  final cached = await MetaOta.cached();
  var local = MetaOta.freshness(asset);
  if (cached != null) {
    final c = MetaOta.freshness(cached);
    if (c.compareTo(local) > 0) local = c;
  }
  final changed = await MetaOta.update(localFreshness: local);
  if (changed) {
    ref.invalidate(metaDbProvider);
    ref.invalidate(syncStatusProvider);
  }
  return changed;
});

/// Applique la mise à jour méta : télécharge, installe, recharge l'app.
/// Retourne true si les données affichées ont réellement changé.
Future<bool> applyMetaUpdate(WidgetRef ref) async {
  final local = await ref.read(metaDbProvider.future);
  final changed = await MetaOta.update(localFreshness: local.freshness);
  if (changed) {
    ref.invalidate(metaDbProvider);
    ref.invalidate(syncStatusProvider);
  }
  return changed;
}
