import "package:flutter/material.dart";

import "../theme.dart";

/// Fond « aurore » : base sombre + lueurs violet / cyan / rose (DA data-tree).
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
    return Stack(
      children: [
        const Positioned.fill(child: ColoredBox(color: kBg)),
        Positioned(left: -140, top: -150, child: _glow(kPurple, 460, 0.16)),
        Positioned(right: -160, bottom: -180, child: _glow(kCyan, 480, 0.10)),
        Positioned(right: 40, top: -120, child: _glow(kPink, 340, 0.08)),
        Positioned.fill(child: child),
      ],
    );
  }
}
