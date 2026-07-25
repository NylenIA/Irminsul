import "dart:convert";

import "package:flutter/services.dart" show rootBundle;
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:http/http.dart" as http;

/// Provenance du moteur de simulation embarqué (écrite par la CI au build).
class EngineInfo {
  final String commit;
  final String shortCommit;
  final DateTime builtAt;
  final String latestRelease;
  final DateTime releasePublished;
  final List<String> extraPRs;

  const EngineInfo({
    required this.commit,
    required this.shortCommit,
    required this.builtAt,
    required this.latestRelease,
    required this.releasePublished,
    required this.extraPRs,
  });

  bool get isLocalDev => commit == "local";

  /// Le moteur embarqué est-il plus récent que la dernière version publiée ?
  bool get aheadOfRelease => builtAt.isAfter(releasePublished);

  int get ageInDays => DateTime.now().toUtc().difference(builtAt).inDays;
}

/// Infos embarquées (assets) — toujours disponibles, même hors-ligne.
final engineInfoProvider = FutureProvider<EngineInfo>((ref) async {
  final raw = await rootBundle.loadString("assets/data/engine_info.json");
  final j = jsonDecode(raw) as Map<String, dynamic>;
  DateTime parse(String? s) =>
      DateTime.tryParse(s ?? "")?.toUtc() ?? DateTime.utc(1970);
  return EngineInfo(
    commit: j["commit"] as String? ?? "?",
    shortCommit: j["shortCommit"] as String? ?? "?",
    builtAt: parse(j["builtAt"] as String?),
    latestRelease: j["latestRelease"] as String? ?? "?",
    releasePublished: parse(j["releasePublished"] as String?),
    extraPRs: (j["extraPRs"] as List? ?? const []).cast<String>(),
  );
});

/// État de fraîcheur du moteur.
enum EngineFreshness { upToDate, outdated, offline, localDev }

class EngineStatus {
  final EngineFreshness state;
  final EngineInfo info;
  final String? liveRelease; // dernière version publiée, vérifiée en direct
  final DateTime? livePublished;
  const EngineStatus(this.state, this.info,
      {this.liveRelease, this.livePublished});
}

/// Vérifie EN DIRECT s'il existe une version de gcsim plus récente que le
/// moteur embarqué (l'app est reconstruite chaque jour, mais on le prouve).
final engineStatusProvider = FutureProvider<EngineStatus>((ref) async {
  final info = await ref.watch(engineInfoProvider.future);
  if (info.isLocalDev) {
    return EngineStatus(EngineFreshness.localDev, info);
  }
  try {
    final resp = await http.get(
      Uri.parse(
          "https://api.github.com/repos/genshinsim/gcsim/releases/latest"),
      headers: {"User-Agent": "Irminsul/0.1"},
    ).timeout(const Duration(seconds: 10));
    if (resp.statusCode != 200) {
      return EngineStatus(EngineFreshness.offline, info);
    }
    final j = jsonDecode(resp.body) as Map<String, dynamic>;
    final tag = j["tag_name"] as String? ?? "?";
    final published =
        DateTime.tryParse(j["published_at"] as String? ?? "")?.toUtc();
    if (published == null) {
      return EngineStatus(EngineFreshness.offline, info);
    }
    // Compilé après la dernière release => on a au moins tout son contenu.
    final ok = info.builtAt.isAfter(published);
    return EngineStatus(
      ok ? EngineFreshness.upToDate : EngineFreshness.outdated,
      info,
      liveRelease: tag,
      livePublished: published,
    );
  } catch (_) {
    return EngineStatus(EngineFreshness.offline, info);
  }
});
