import "dart:math";

import "package:flutter/material.dart";

/// Balayage « données Irminsul » pendant les transitions : une fine bande
/// d'énergie verticale traverse l'écran, semée de nœuds lumineux (façon
/// dendrite / flux de données). Bref, sobre, dans la charte (≤ 400 ms).
class DataSweep extends StatelessWidget {
  final Animation<double> animation;
  const DataSweep({super.key, required this.animation});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return IgnorePointer(
      child: AnimatedBuilder(
        animation: animation,
        builder: (context, _) {
          final t = animation.value;
          if (t <= 0 || t >= 1) return const SizedBox.shrink();
          return CustomPaint(
            size: Size.infinite,
            painter: _SweepPainter(
              progress: t,
              a: cs.primary,
              b: cs.tertiary,
            ),
          );
        },
      ),
    );
  }
}

class _SweepPainter extends CustomPainter {
  final double progress;
  final Color a;
  final Color b;
  _SweepPainter({required this.progress, required this.a, required this.b});

  // Positions fixes (graine stable) pour un rendu propre à chaque passage.
  static final _rnd = Random(21);
  static final List<double> _nodeYs =
      List.generate(9, (_) => 0.06 + _rnd.nextDouble() * 0.88);
  static final List<double> _nodeSizes =
      List.generate(9, (_) => 1.6 + _rnd.nextDouble() * 2.4);

  @override
  void paint(Canvas canvas, Size size) {
    // La bande traverse de gauche à droite ; visible surtout au milieu.
    final x = size.width * (progress * 1.2 - 0.1);
    final vis = sin(progress * pi); // fondu entrée/sortie
    if (vis <= 0) return;

    // Bande lumineuse (dégradé vertical accent -> tertiaire).
    final band = Rect.fromLTWH(x - 30, 0, 60, size.height);
    canvas.drawRect(
      band,
      Paint()
        ..shader = LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            a.withValues(alpha: 0),
            a.withValues(alpha: 0.10 * vis),
            b.withValues(alpha: 0.14 * vis),
            a.withValues(alpha: 0.10 * vis),
            a.withValues(alpha: 0),
          ],
        ).createShader(band),
    );

    // Ligne centrale fine.
    canvas.drawLine(
      Offset(x, 0),
      Offset(x, size.height),
      Paint()
        ..color = b.withValues(alpha: 0.35 * vis)
        ..strokeWidth = 1.2,
    );

    // Nœuds de données le long de la ligne (petits halos).
    for (var i = 0; i < _nodeYs.length; i++) {
      final y = size.height * _nodeYs[i];
      final r = _nodeSizes[i];
      final wob = sin(progress * 2 * pi + i) * 5; // léger décalage organique
      canvas.drawCircle(
        Offset(x + wob, y),
        r * 2.6,
        Paint()..color = b.withValues(alpha: 0.10 * vis),
      );
      canvas.drawCircle(
        Offset(x + wob, y),
        r,
        Paint()..color = Colors.white.withValues(alpha: 0.55 * vis),
      );
    }
  }

  @override
  bool shouldRepaint(_SweepPainter old) => old.progress != progress;
}
