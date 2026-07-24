import "package:flutter/material.dart";

/// Apparition « cascade » : fondu + léger glissement vers le haut, avec délai.
/// Vocabulaire d'animation commun de l'app (sobre, 200-400 ms, easeOutCubic).
class Reveal extends StatefulWidget {
  final Widget child;
  final int delayMs;
  final Duration duration;

  const Reveal({
    super.key,
    required this.child,
    this.delayMs = 0,
    this.duration = const Duration(milliseconds: 380),
  });

  @override
  State<Reveal> createState() => _RevealState();
}

class _RevealState extends State<Reveal> with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final CurvedAnimation _a;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(vsync: this, duration: widget.duration);
    _a = CurvedAnimation(parent: _c, curve: Curves.easeOutCubic);
    Future.delayed(Duration(milliseconds: widget.delayMs), () {
      if (mounted) _c.forward();
    });
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _a,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.05),
          end: Offset.zero,
        ).animate(_a),
        child: widget.child,
      ),
    );
  }
}

/// Compteur animé (le chiffre « monte » jusqu'à sa valeur).
class CountUp extends StatelessWidget {
  final num value;
  final TextStyle? style;
  final Duration duration;
  final String Function(num) format;

  const CountUp({
    super.key,
    required this.value,
    this.style,
    this.duration = const Duration(milliseconds: 900),
    this.format = _defaultFormat,
  });

  static String _defaultFormat(num v) {
    final s = v.round().toString();
    final buf = StringBuffer();
    for (var i = 0; i < s.length; i++) {
      if (i > 0 && (s.length - i) % 3 == 0) buf.write(" ");
      buf.write(s[i]);
    }
    return buf.toString();
  }

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: value.toDouble()),
      duration: duration,
      curve: Curves.easeOutCubic,
      builder: (context, v, _) => Text(format(v), style: style),
    );
  }
}
