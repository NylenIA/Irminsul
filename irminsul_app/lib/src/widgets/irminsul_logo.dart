import "package:flutter/material.dart";
import "package:flutter_svg/flutter_svg.dart";

import "../theme.dart";

/// Logo Irminsul (SVG vectoriel) avec, en option, une lueur qui « respire ».
class IrminsulLogo extends StatefulWidget {
  final double size;
  final bool animated;
  const IrminsulLogo({super.key, this.size = 64, this.animated = true});

  @override
  State<IrminsulLogo> createState() => _IrminsulLogoState();
}

class _IrminsulLogoState extends State<IrminsulLogo>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );
    if (widget.animated) _c.repeat(reverse: true);
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
    return AnimatedBuilder(
      animation: _c,
      builder: (context, _) {
        final v = 0.4 + 0.6 * Curves.easeInOut.transform(_c.value);
        return Stack(
          alignment: Alignment.center,
          children: [
            Container(
              width: widget.size * 0.62,
              height: widget.size * 0.62,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: kCyan.withValues(alpha: 0.22 * v),
                    blurRadius: 34 * v,
                    spreadRadius: 4 * v,
                  ),
                  BoxShadow(
                    color: kPurple.withValues(alpha: 0.30 * v),
                    blurRadius: 46 * v,
                    spreadRadius: 6 * v,
                  ),
                ],
              ),
            ),
            logo,
          ],
        );
      },
    );
  }
}
