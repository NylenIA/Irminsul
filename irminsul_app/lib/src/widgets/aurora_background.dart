import "package:flutter/material.dart";

import "../theme.dart";

/// Fond « aurore » : base sombre + lueurs. Par défaut aux couleurs du thème ;
/// peut être teinté par onglet (cohérence de section).
class AuroraBackground extends StatelessWidget {
  final Widget child;
  final Color? tintA;
  final Color? tintB;
  final Color? tintC;
  const AuroraBackground({
    super.key,
    required this.child,
    this.tintA,
    this.tintB,
    this.tintC,
  });

  Widget _glow(Color c, double size, double opacity) => IgnorePointer(
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [c.withValues(alpha: opacity), c.withValues(alpha: 0)],
            ),
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final a = tintA ?? cs.primary;
    final b = tintB ?? cs.tertiary;
    final c3 = tintC ?? cs.secondary;
    return Stack(
      children: [
        const Positioned.fill(child: ColoredBox(color: kBg)),
        AnimatedPositioned(
          duration: const Duration(milliseconds: 600),
          left: -140,
          top: -150,
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 600),
            child: _glow(a, 460, 0.16),
          ),
        ),
        Positioned(right: -160, bottom: -180, child: _glow(b, 480, 0.10)),
        Positioned(right: 40, top: -120, child: _glow(c3, 340, 0.08)),
        Positioned.fill(child: child),
      ],
    );
  }
}
