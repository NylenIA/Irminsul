import "dart:io";

import "package:http/http.dart" as http;
import "package:path_provider/path_provider.dart";

/// Cache disque des icônes de persos (CDN Enka), avec déduplication mémoire.
/// Hors-ligne : si l'icône est déjà en cache elle s'affiche, sinon repli
/// gracieux (initiales) côté widget.
class IconCache {
  static final Map<String, Future<File?>> _pending = {};

  static Future<File?> get(String icon) =>
      _pending.putIfAbsent(icon, () => _load(icon));

  static Future<File?> _load(String icon) async {
    try {
      final dir = await getApplicationSupportDirectory();
      final f = File("${dir.path}/icons/$icon.png");
      if (await f.exists()) return f;
      final resp = await http.get(
        Uri.parse("https://enka.network/ui/UI_AvatarIcon_$icon.png"),
        headers: {"User-Agent": "Irminsul/0.1 (github.com/NylenIA/Irminsul)"},
      ).timeout(const Duration(seconds: 12));
      if (resp.statusCode != 200) return null;
      await f.create(recursive: true);
      await f.writeAsBytes(resp.bodyBytes);
      return f;
    } catch (_) {
      return null;
    }
  }
}
