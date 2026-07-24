import "package:flutter/material.dart";

/// Reflet doré qui balaye lentement (cartes 5★ / Archons). Sobre : bande
/// diagonale translucide qui traverse toutes les 4 s.
class GoldShimmer extends StatefulWidget {
  final Widget child;
  final BorderRadius borderRadius;
  const GoldShimmer({
    super.key,
    required this.child,
    this.borderRadius = const BorderRadius.all(Radius.circular(20)),
  });

  @override
  State<GoldShimmer> createState() => _GoldShimmerState();
}

class _GoldShimmerState extends State<GoldShimmer>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(vsync: this, duration: const Duration(seconds: 4))
      ..repeat();
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: widget.borderRadius,
      child: Stack(
        children: [
          widget.child,
          Positioned.fill(
            child: IgnorePointer(
              child: AnimatedBuilder(
                animation: _c,
                builder: (context, _) {
                  return LayoutBuilder(builder: (context, cons) {
                    final w = cons.maxWidth;
                    final x = (w + 300) * _c.value - 150;
                    return Stack(
                      children: [
                        Positioned(
                          left: x,
                          top: -40,
                          bottom: -40,
                          child: Transform.rotate(
                            angle: 0.35,
                            child: Container(
                              width: 70,
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  begin: Alignment.centerLeft,
                                  end: Alignment.centerRight,
                                  colors: [
                                    const Color(0x00F6D27A),
                                    const Color(0xFFF6D27A)
                                        .withValues(alpha: 0.10),
                                    const Color(0x00F6D27A),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    );
                  });
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
