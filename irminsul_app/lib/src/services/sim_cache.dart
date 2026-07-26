import "dart:convert";

import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:shared_preferences/shared_preferences.dart";

import "gcsim_service.dart";

/// Résultat de simulation mis en cache (par équipe, lié à la box importée).
class CachedSim {
  final int dps;
  final double dpsMin;
  final double dpsMax;
  final String boxLabel; // invalide si la box change
  final DateTime at;

  const CachedSim({
    required this.dps,
    required this.dpsMin,
    required this.dpsMax,
    required this.boxLabel,
    required this.at,
  });

  Map<String, dynamic> toJson() => {
        "dps": dps,
        "min": dpsMin,
        "max": dpsMax,
        "box": boxLabel,
        "at": at.toIso8601String(),
      };

  static CachedSim fromJson(Map<String, dynamic> m) => CachedSim(
        dps: (m["dps"] as num).toInt(),
        dpsMin: (m["min"] as num).toDouble(),
        dpsMax: (m["max"] as num).toDouble(),
        boxLabel: m["box"] as String? ?? "",
        at: DateTime.tryParse(m["at"] as String? ?? "") ?? DateTime(1970),
      );
}

class SimCache {
  static const _key = "sim_cache_v1";

  static Future<Map<String, CachedSim>> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null) return {};
    try {
      final j = jsonDecode(raw) as Map<String, dynamic>;
      return j.map((k, v) =>
          MapEntry(k, CachedSim.fromJson(v as Map<String, dynamic>)));
    } catch (_) {
      return {};
    }
  }

  static Future<void> put(
      String teamId, SimResult r, String boxLabel) async {
    final prefs = await SharedPreferences.getInstance();
    final all = await load();
    all[teamId] = CachedSim(
      dps: r.dps,
      dpsMin: r.dpsMin,
      dpsMax: r.dpsMax,
      boxLabel: boxLabel,
      at: DateTime.now(),
    );
    await prefs.setString(
        _key, jsonEncode(all.map((k, v) => MapEntry(k, v.toJson()))));
  }
}

/// Cache des simulations par équipe. Invalider après chaque nouvelle sim.
final simCacheProvider =
    FutureProvider<Map<String, CachedSim>>((ref) => SimCache.load());
