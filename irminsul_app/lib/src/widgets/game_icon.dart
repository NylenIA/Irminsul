import "dart:io";

import "package:flutter/material.dart";

import "../services/icon_cache.dart";

/// Icône du jeu générique (aptitude, constellation, arme, set d'artefacts) :
/// carré arrondi sombre, image en cache, repli sur un glyphe.
class GameIcon extends StatelessWidget {
  final String filename;
  final double size;
  final IconData fallback;
  final Color? tint;

  const GameIcon({
    super.key,
    required this.filename,
    this.size = 44,
    this.fallback = Icons.auto_awesome,
    this.tint,
  });

  @override
  Widget build(BuildContext context) {
    final accent = tint ?? Theme.of(context).colorScheme.primary;
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(size * 0.24),
        border: Border.all(color: Colors.white.withValues(alpha: 0.10)),
      ),
      clipBehavior: Clip.antiAlias,
      child: FutureBuilder<File?>(
        future: IconCache.get(filename),
        builder: (context, snap) {
          final file = snap.data;
          if (file == null) {
            return Icon(fallback,
                size: size * 0.45, color: accent.withValues(alpha: 0.7));
          }
          return Padding(
            padding: EdgeInsets.all(size * 0.08),
            child: Image.file(file, fit: BoxFit.contain),
          );
        },
      ),
    );
  }
}
