import "dart:convert";
import "dart:io";

import "package:http/http.dart" as http;
import "package:path_provider/path_provider.dart";

/// Source de vérité distante : la BDD méta de la branche de l'app sur GitHub.
/// Même principe que le moteur : les DONNÉES vivent hors du binaire, donc un
/// nouveau cycle d'Abîme ou une correction méta n'oblige pas à re-télécharger
/// l'app. Le fichier distant n'est que du JSON (aucun code exécuté).
const metaRemoteUrl =
    "https://raw.githubusercontent.com/NylenIA/Irminsul/flutter-app/irminsul_app/assets/data/meta_teams.json";

/// Mise à jour « over-the-air » de la BDD méta.
class MetaOta {
  static const _fileName = "meta_teams_ota.json";

  static Future<File> _file() async {
    final dir = await getApplicationSupportDirectory();
    return File("${dir.path}${Platform.pathSeparator}$_fileName");
  }

  /// Clé de fraîcheur d'un JSON méta, **comparable telle quelle** avec
  /// `compareTo` : date du contenu de cycle (ISO — elle bouge à chaque
  /// Abîme/Théâtre même quand la version du jeu ne bouge pas), puis la version
  /// zéro-paddée pour que 6.10 passe bien après 6.7.
  /// Une méta sans date de contenu vaut « 0000-00-00 » : elle ne peut donc
  /// jamais écraser une méta datée.
  static String freshness(Map<String, dynamic> json) {
    final c = json["content"] as Map<String, dynamic>?;
    final raw = (c?["updated"] as String? ?? "").trim();
    final updated = raw.isEmpty ? "0000-00-00" : raw;
    final version = (json["metaVersion"] as String? ?? "0").trim();
    final padded = version
        .split(".")
        .map((p) => (int.tryParse(p.trim()) ?? 0).toString().padLeft(4, "0"))
        .join(".");
    return "$updated|$padded";
  }

  /// Valide la structure minimale avant d'accepter un JSON distant.
  static Map<String, dynamic>? validate(String raw) {
    try {
      final json = jsonDecode(raw) as Map<String, dynamic>;
      if (json["metaVersion"] is! String) return null;
      final teams = json["teams"];
      if (teams is! List || teams.isEmpty) return null;
      for (final t in teams) {
        if (t is! Map || t["id"] is! String || t["mode"] is! String) {
          return null;
        }
      }
      return json;
    } catch (_) {
      return null;
    }
  }

  /// JSON méta mis en cache localement (null si absent ou corrompu).
  static Future<Map<String, dynamic>?> cached() async {
    try {
      final f = await _file();
      if (!await f.exists()) return null;
      return validate(await f.readAsString());
    } catch (_) {
      return null;
    }
  }

  /// Télécharge la méta distante. Retourne le JSON validé, ou null (offline,
  /// HTTP != 200, JSON invalide) — dans ce cas l'app garde ce qu'elle a.
  static Future<Map<String, dynamic>?> download() async {
    try {
      final resp = await http
          .get(Uri.parse(metaRemoteUrl))
          .timeout(const Duration(seconds: 15));
      if (resp.statusCode != 200) return null;
      return validate(utf8.decode(resp.bodyBytes));
    } catch (_) {
      return null;
    }
  }

  /// Télécharge ET installe si le distant est plus frais que l'installé.
  /// Retourne true si le cache local a effectivement changé.
  static Future<bool> update({required String localFreshness}) async {
    final remote = await download();
    if (remote == null) return false;
    if (freshness(remote).compareTo(localFreshness) <= 0) return false;
    try {
      final f = await _file();
      await f.writeAsString(jsonEncode(remote));
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Efface la méta téléchargée (retour à celle embarquée dans le build).
  static Future<void> clear() async {
    try {
      final f = await _file();
      if (await f.exists()) await f.delete();
    } catch (_) {
      /* rien à faire : on retombe sur l'asset embarqué */
    }
  }
}
