import "package:flutter/material.dart";

/// Survol subtil : léger zoom + lueur d'accent. Jamais too much.
class HoverCard extends StatefulWidget {
  final Widget child;
  final Color? glow;
  const HoverCard({super.key, required this.child, this.glow});

  @override
  State<HoverCard> createState() => _HoverCardState();
}

class _HoverCardState extends State<HoverCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final glow = widget.glow ?? Theme.of(context).colorScheme.primary;
    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedScale(
        scale: _hover ? 1.015 : 1.0,
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOutCubic,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            boxShadow: _hover
                ? [
                    BoxShadow(
                      color: glow.withValues(alpha: 0.16),
                      blurRadius: 26,
                      spreadRadius: 1,
                    ),
                  ]
                : const [],
          ),
          child: widget.child,
        ),
      ),
    );
  }
}
