import "dart:io";

import "package:flutter/material.dart";

import "../services/icon_cache.dart";
import "../theme.dart";

/// Portrait de perso : vraie image (CDN Enka, cachée sur disque) dans un cadre
/// à l'anneau couleur d'élément ; repli initiales si hors-ligne.
class CharIcon extends StatelessWidget {
  final String name;
  final String icon;
  final String element;
  final double size;
  final bool dimmed;
  final bool showName;

  const CharIcon({
    super.key,
    required this.name,
    required this.icon,
    required this.element,
    this.size = 52,
    this.dimmed = false,
    this.showName = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = elementColor(element);
    final frame = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: dimmed ? 0.03 : 0.06),
        borderRadius: BorderRadius.circular(size * 0.29),
        border: Border.all(
          color: color.withValues(alpha: dimmed ? 0.3 : 0.8),
          width: 1.6,
        ),
        boxShadow: dimmed
            ? const []
            : [
                BoxShadow(
                  color: color.withValues(alpha: 0.18),
                  blurRadius: 12,
                ),
              ],
      ),
      clipBehavior: Clip.antiAlias,
      child: FutureBuilder<File?>(
        future: IconCache.get(icon),
        builder: (context, snap) {
          final file = snap.data;
          if (file == null) {
            return Center(
              child: Text(
                name.length >= 2
                    ? name.substring(0, 2).toUpperCase()
                    : name.toUpperCase(),
                style: TextStyle(
                  fontSize: size * 0.27,
                  fontWeight: FontWeight.w800,
                  color: dimmed ? Colors.white38 : Colors.white,
                ),
              ),
            );
          }
          return AnimatedOpacity(
            opacity: 1,
            duration: const Duration(milliseconds: 250),
            child: ColorFiltered(
              colorFilter: dimmed
                  ? const ColorFilter.matrix(<double>[
                      0.2126, 0.7152, 0.0722, 0, 0,
                      0.2126, 0.7152, 0.0722, 0, 0,
                      0.2126, 0.7152, 0.0722, 0, 0,
                      0, 0, 0, 0.55, 0,
                    ])
                  : const ColorFilter.mode(
                      Colors.transparent, BlendMode.dst),
              child: Image.file(file, fit: BoxFit.cover),
            ),
          );
        },
      ),
    );

    if (!showName) return frame;
    return Column(
      children: [
        frame,
        const SizedBox(height: 6),
        Text(
          name,
          style: TextStyle(
            fontSize: 11,
            color: Colors.white.withValues(alpha: dimmed ? 0.35 : 0.6),
          ),
        ),
      ],
    );
  }
}
