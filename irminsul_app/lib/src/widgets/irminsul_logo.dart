import "dart:math";

import "package:flutter/material.dart";
import "package:flutter_svg/flutter_svg.dart";

import "../theme.dart";

/// Logo Irminsul (SVG) avec animation « énergie » : particules qui remontent
/// le long de l'arbre + lueur qui respire. Couleurs Irminsul (fixes).
class IrminsulLogo extends StatefulWidget {
  final double size;
  final bool animated;
  const IrminsulLogo({super.key, this.size = 64, this.animated = true});

  @override
  State<IrminsulLogo> createState() => _IrminsulLogoState();
}

class _Mote {
  final double x; // 0..1 (position horizontale de base)
  final double r;
  final double offset; // décalage de phase
  final double wiggle;
  final double maxOpacity;
  final Color color;
  const _Mote(
      this.x, this.r, this.offset, this.wiggle, this.maxOpacity, this.color);
}

class _IrminsulLogoState extends State<IrminsulLogo>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final List<_Mote> _motes;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(vsync: this, duration: const Duration(seconds: 6));
    if (widget.animated) _c.repeat();
    final rnd = Random(7);
    const colors = [kCyan, kPurple, Color(0xFFE9D5FF)];
    _motes = List.generate(18, (i) {
      return _Mote(
        0.18 + rnd.nextDouble() * 0.64,
        1.1 + rnd.nextDouble() * 2.1,
        rnd.nextDouble(),
        0.5 + rnd.nextDouble() * 1.2,
        0.25 + rnd.nextDouble() * 0.45,
        colors[i % colors.length],
      );
    });
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final logo = SvgPicture.asset(
      "assets/irminsul_logo.svg",
      width: widget.size,
      height: widget.size,
    );
    if (!widget.animated) {
      return SizedBox(width: widget.size, height: widget.size, child: logo);
    }

    final box = widget.size * 1.6;
    return AnimatedBuilder(
      animation: _c,
      builder: (context, _) {
        final t = _c.value;
        final glow = 0.4 + 0.6 * (0.5 + 0.5 * sin(t * 2 * pi));
        return SizedBox(
          width: box,
          height: box,
          child: Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: widget.size * 0.6,
                height: widget.size * 0.6,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: kCyan.withValues(alpha: 0.22 * glow),
                      blurRadius: 34 * glow,
                      spreadRadius: 4 * glow,
                    ),
                    BoxShadow(
                      color: kPurple.withValues(alpha: 0.30 * glow),
                      blurRadius: 48 * glow,
                      spreadRadius: 6 * glow,
                    ),
                  ],
                ),
              ),
              CustomPaint(
                size: Size(box, box),
                painter: _MotesPainter(t, _motes),
              ),
              SizedBox(width: widget.size, height: widget.size, child: logo),
            ],
          ),
        );
      },
    );
  }
}

class _MotesPainter extends CustomPainter {
  final double t;
  final List<_Mote> motes;
  _MotesPainter(this.t, this.motes);

  @override
  void paint(Canvas canvas, Size size) {
    for (final m in motes) {
      final prog = (t + m.offset) % 1.0;
      // Monte du bas vers le haut (le long de l'arbre).
      final y = size.height * (0.9 - 0.8 * prog);
      final x = size.width * m.x + sin(prog * 2 * pi * m.wiggle) * 7;
      final opacity = sin(prog * pi) * m.maxOpacity; // fondu entrée/sortie
      if (opacity <= 0) continue;
      final paint = Paint()
        ..color = m.color.withValues(alpha: opacity.clamp(0.0, 1.0));
      canvas.drawCircle(Offset(x, y), m.r * (0.6 + prog * 0.7), paint);
    }
  }

  @override
  bool shouldRepaint(_MotesPainter old) => old.t != t;
}
