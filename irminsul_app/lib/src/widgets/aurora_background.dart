import "package:flutter/material.dart";

import "../theme.dart";

/// Fond « aurore » : base sombre + lueurs qui suivent l'accent du thème.
class AuroraBackground extends StatelessWidget {
  final Widget child;
  const AuroraBackground({super.key, required this.child});

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
    return Stack(
      children: [
        const Positioned.fill(child: ColoredBox(color: kBg)),
        Positioned(left: -140, top: -150, child: _glow(cs.primary, 460, 0.16)),
        Positioned(right: -160, bottom: -180, child: _glow(cs.tertiary, 480, 0.10)),
        Positioned(right: 40, top: -120, child: _glow(cs.secondary, 340, 0.08)),
        Positioned.fill(child: child),
      ],
    );
  }
}
