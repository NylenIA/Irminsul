import "dart:math";

import "package:flutter/material.dart";

import "../theme.dart";

class _MotionPreset {
  final List<Color> colors;
  final double dy; // -1 monte, +1 tombe, 0 horizontal
  final double wiggle; // amplitude latérale (px)
  final double speed; // vitesse relative
  final bool jitter; // tremblement (electro)
  const _MotionPreset(this.colors, this.dy, this.wiggle, this.speed,
      {this.jitter = false});
}

const _presets = <String, _MotionPreset>{
  "pyro": _MotionPreset(
      [Color(0xFFFF6A4D), Color(0xFFF59E0B), Color(0xFFFFD9A0)], -1, 10, 1.3),
  "hydro": _MotionPreset(
      [Color(0xFF3FB6FF), Color(0xFF22D3EE), Color(0xFFBDE9FF)], 1, 8, 0.7),
  "cryo": _MotionPreset(
      [Color(0xFF8FE3EA), Color(0xFFDDF7FA), Color(0xFFB5EDF2)], 1, 26, 0.45),
  "electro": _MotionPreset(
      [Color(0xFFB98BFF), Color(0xFFE879F9), Color(0xFFD8C6FF)], -1, 6, 1.6,
      jitter: true),
  "anemo": _MotionPreset(
      [Color(0xFF6FD6B6), Color(0xFF9BE8D2), Color(0xFF22D3EE)], 0, 40, 0.9),
  "geo": _MotionPreset(
      [Color(0xFFF2C14E), Color(0xFFFDE68A), Color(0xFFFFF3C9)], -1, 4, 0.35),
  "dendro": _MotionPreset(
      [Color(0xFF9AD24F), Color(0xFFB5E48C), Color(0xFF2DD4BF)], -1, 30, 0.8),
  "none": _MotionPreset([kPurple, kCyan, Color(0xFFE9D5FF)], -1, 14, 0.7),
};

const _gold = Color(0xFFF6D27A);

class _Mote {
  final double x0, y0, size, phase, speedVar;
  const _Mote(this.x0, this.y0, this.size, this.phase, this.speedVar);
}

/// Fond animé thématique par élément : SYMBOLE de l'élément en filigrane
/// (rotation/pulsation lentes) + particules bien visibles. L'intensité suit
/// la rareté ; les Archons reçoivent des éclats dorés.
class ElementBackdrop extends StatefulWidget {
  final String element;
  final Widget child;
  final int intensity; // nombre de particules
  final bool golden; // éclats dorés (Archons)
  final Color? glowA; // teinte d'ambiance (nation) — sinon élément
  final Color? glowB;
  const ElementBackdrop({
    super.key,
    required this.element,
    required this.child,
    this.intensity = 30,
    this.golden = false,
    this.glowA,
    this.glowB,
  });

  @override
  State<ElementBackdrop> createState() => _ElementBackdropState();
}

class _ElementBackdropState extends State<ElementBackdrop>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final List<_Mote> _motes;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
        vsync: this, duration: const Duration(seconds: 12))
      ..repeat();
    final rnd = Random(widget.element.hashCode);
    _motes = List.generate(widget.intensity, (_) {
      return _Mote(
        rnd.nextDouble(),
        rnd.nextDouble(),
        1.4 + rnd.nextDouble() * 3.2,
        rnd.nextDouble(),
        0.6 + rnd.nextDouble() * 0.8,
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
    var preset = _presets[widget.element] ?? _presets["none"]!;
    if (widget.golden) {
      preset = _MotionPreset(
        [...preset.colors, _gold, _gold],
        preset.dy,
        preset.wiggle,
        preset.speed,
        jitter: preset.jitter,
      );
    }
    final glow = elementColor(widget.element);
    final ambA = widget.glowA ?? glow;
    final ambB = widget.glowB ?? glow;
    final hasSymbol = widget.element != "none";

    return Stack(
      children: [
        // lueur d'ambiance (nation ou élément) — haut de page
        Positioned(
          top: -140,
          left: 60,
          child: IgnorePointer(
            child: Container(
              width: 480,
              height: 480,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(colors: [
                  ambA.withValues(alpha: 0.14),
                  ambA.withValues(alpha: 0),
                ]),
              ),
            ),
          ),
        ),
        Positioned(
          bottom: -160,
          left: -120,
          child: IgnorePointer(
            child: Container(
              width: 420,
              height: 420,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(colors: [
                  ambB.withValues(alpha: 0.10),
                  ambB.withValues(alpha: 0),
                ]),
              ),
            ),
          ),
        ),
        // SYMBOLE de l'élément en filigrane (respiration + rotation lente)
        if (hasSymbol)
          Positioned(
            right: -70,
            bottom: -50,
            child: IgnorePointer(
              child: AnimatedBuilder(
                animation: _c,
                builder: (context, _) {
                  final t = _c.value;
                  final pulse = 0.06 + 0.035 * sin(t * 2 * pi);
                  return Transform.rotate(
                    angle: sin(t * 2 * pi) * 0.06,
                    child: Opacity(
                      opacity: pulse + (widget.golden ? 0.02 : 0),
                      child: Image.asset(
                        "assets/elements/${widget.element}.png",
                        width: 440,
                        height: 440,
                        color: glow,
                        colorBlendMode: BlendMode.srcIn,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        Positioned.fill(
          child: IgnorePointer(
            child: AnimatedBuilder(
              animation: _c,
              builder: (context, _) => CustomPaint(
                painter: _BackdropPainter(_c.value, _motes, preset),
              ),
            ),
          ),
        ),
        widget.child,
      ],
    );
  }
}

class _BackdropPainter extends CustomPainter {
  final double t;
  final List<_Mote> motes;
  final _MotionPreset p;
  _BackdropPainter(this.t, this.motes, this.p);

  @override
  void paint(Canvas canvas, Size size) {
    for (var i = 0; i < motes.length; i++) {
      final m = motes[i];
      final prog = (t * p.speed * m.speedVar + m.phase) % 1.0;

      double x, y;
      if (p.dy == 0) {
        x = size.width * ((m.x0 + prog) % 1.0);
        y = size.height * m.y0 +
            sin(prog * 2 * pi + m.phase * 6) * p.wiggle;
      } else {
        y = size.height * ((m.y0 + prog * p.dy) % 1.0);
        if (y < 0) y += size.height;
        x = size.width * m.x0 + sin(prog * 2 * pi * 2 + m.phase * 6) * p.wiggle;
      }
      if (p.jitter) {
        x += sin(t * 60 * pi + i * 3) * 2.2;
        y += cos(t * 52 * pi + i * 5) * 2.2;
      }

      final vis = sin(prog * pi) *
          (0.55 + 0.45 * sin(t * 8 * pi + m.phase * 9)).clamp(0.35, 1.0);
      if (vis <= 0.02) continue;

      final color = p.colors[i % p.colors.length];
      canvas.drawCircle(
        Offset(x, y),
        m.size * 3.0,
        Paint()..color = color.withValues(alpha: 0.10 * vis),
      );
      canvas.drawCircle(
        Offset(x, y),
        m.size,
        Paint()..color = color.withValues(alpha: (0.55 * vis).clamp(0, 1)),
      );
    }
  }

  @override
  bool shouldRepaint(_BackdropPainter old) => old.t != t;
}
