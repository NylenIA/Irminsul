import "dart:convert";

import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:http/http.dart" as http;

import "../data/meta_repository.dart";

/// État de synchronisation des données méta (principe OTA : le code est séparé
/// des données ; la référence vit sur GitHub et l'app compare au démarrage).
enum SyncState { upToDate, updateAvailable, offline }

class SyncStatus {
  final SyncState state;
  final String localVersion;
  final String? remoteVersion;
  const SyncStatus(this.state, this.localVersion, this.remoteVersion);
}

/// Source de vérité distante : la BDD méta de la branche de l'app sur GitHub.
const _remoteMetaUrl =
    "https://raw.githubusercontent.com/NylenIA/Irminsul/flutter-app/irminsul_app/assets/data/meta_teams.json";

final syncStatusProvider = FutureProvider<SyncStatus>((ref) async {
  final local = await ref.watch(metaDbProvider.future);
  try {
    final resp = await http
        .get(Uri.parse(_remoteMetaUrl))
        .timeout(const Duration(seconds: 10));
    if (resp.statusCode != 200) {
      return SyncStatus(SyncState.offline, local.metaVersion, null);
    }
    final remote = (jsonDecode(resp.body)
        as Map<String, dynamic>)["metaVersion"] as String?;
    if (remote == null) {
      return SyncStatus(SyncState.offline, local.metaVersion, null);
    }
    return SyncStatus(
      remote == local.metaVersion
          ? SyncState.upToDate
          : SyncState.updateAvailable,
      local.metaVersion,
      remote,
    );
  } catch (_) {
    return SyncStatus(SyncState.offline, local.metaVersion, null);
  }
});
