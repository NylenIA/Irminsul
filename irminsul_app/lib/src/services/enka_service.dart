import "dart:convert";

import "package:http/http.dart" as http;

/// Résultat d'un import Enka.
class EnkaResult {
  final String nickname;
  final int level;
  final int characterCount;
  const EnkaResult({
    required this.nickname,
    required this.level,
    required this.characterCount,
  });
}

/// Erreur lisible pour l'UI.
class EnkaException implements Exception {
  final String message;
  const EnkaException(this.message);
  @override
  String toString() => message;
}

/// Import de la vitrine via l'API publique Enka.network.
/// NOTE : Enka n'expose que les persos de la VITRINE (max ~12), pas toute la box.
class EnkaService {
  static const _base = "https://enka.network/api/uid";

  Future<EnkaResult> fetch(String uid) async {
    final cleaned = uid.trim();
    if (cleaned.isEmpty || int.tryParse(cleaned) == null) {
      throw const EnkaException("UID invalide (chiffres uniquement).");
    }
    final http.Response resp;
    try {
      resp = await http.get(
        Uri.parse("$_base/$cleaned"),
        headers: {"User-Agent": "Irminsul/0.1 (github.com/NylenIA/Irminsul)"},
      ).timeout(const Duration(seconds: 12));
    } catch (_) {
      throw const EnkaException(
          "Enka.network injoignable (connexion ?). Réessaie.");
    }

    switch (resp.statusCode) {
      case 200:
        break;
      case 404:
        throw const EnkaException("UID introuvable sur Enka.network.");
      case 429:
        throw const EnkaException("Trop de requêtes — attends un peu.");
      default:
        throw EnkaException("Enka a répondu ${resp.statusCode}.");
    }

    final json = jsonDecode(resp.body) as Map<String, dynamic>;
    final player = json["playerInfo"] as Map<String, dynamic>?;
    if (player == null) {
      throw const EnkaException("Réponse Enka inattendue.");
    }
    final avatars = json["avatarInfoList"] as List? ?? const [];
    if (avatars.isEmpty) {
      throw const EnkaException(
          "Vitrine vide ou masquée — active « Afficher les détails » en jeu.");
    }
    return EnkaResult(
      nickname: player["nickname"] as String? ?? "Voyageur",
      level: player["level"] as int? ?? 0,
      characterCount: avatars.length,
    );
  }
}
