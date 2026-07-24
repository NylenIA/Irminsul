import "dart:io";

import "package:http/http.dart" as http;
import "package:path_provider/path_provider.dart";

/// Cache disque des icônes du jeu (persos, aptitudes, constellations, armes,
/// artefacts). Essaie le CDN Enka puis les assets Ambr en secours ; dédup
/// mémoire ; hors-ligne : ce qui est en cache s'affiche, sinon repli côté UI.
class IconCache {
  static final Map<String, Future<File?>> _pending = {};

  /// [filename] : nom complet d'asset du jeu (ex. UI_AvatarIcon_Mavuika,
  /// Skill_S_Mavuika_01, UI_EquipIcon_Sword_Falcon, UI_RelicIcon_15032_4).
  static Future<File?> get(String filename) =>
      _pending.putIfAbsent(filename, () => _load(filename));

  static Future<File?> _load(String filename) async {
    if (filename.isEmpty) return null;
    try {
      final dir = await getApplicationSupportDirectory();
      final f = File("${dir.path}/icons/$filename.png");
      if (await f.exists()) return f;

      for (final url in [
        "https://enka.network/ui/$filename.png",
        "https://gi.yatta.moe/assets/UI/$filename.png",
        "https://api.ambr.top/assets/UI/$filename.png",
      ]) {
        try {
          final resp = await http.get(
            Uri.parse(url),
            headers: {
              "User-Agent": "Irminsul/0.1 (github.com/NylenIA/Irminsul)",
            },
          ).timeout(const Duration(seconds: 12));
          if (resp.statusCode == 200 && resp.bodyBytes.isNotEmpty) {
            await f.create(recursive: true);
            await f.writeAsBytes(resp.bodyBytes);
            return f;
          }
        } catch (_) {
          // essaie l'URL suivante
        }
      }
      return null;
    } catch (_) {
      return null;
    }
  }
}
