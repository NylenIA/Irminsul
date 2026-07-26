import "package:flutter/material.dart";

import "../data/meta_repository.dart";
import "../i18n/strings.dart";

/// Bannière « contenu actuel » d'un mode : cycle en cours, points clés,
/// stratégie adéquate, et la meilleure option de la box du joueur.
class ContentBanner extends StatelessWidget {
  final String mode; // abyss | theater | onslaught
  final CurrentContent content;
  final String? bestTeamName;
  final L l;

  const ContentBanner({
    super.key,
    required this.mode,
    required this.content,
    required this.bestTeamName,
    required this.l,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final mc = content.byMode[mode];
    if (mc == null) return const SizedBox.shrink();

    final modeLabel = switch (mode) {
      "abyss" => l.t("modeAbyss"),
      "theater" => l.t("modeTheater"),
      _ => l.t("modeOnslaught"),
    };

    // État réel du cycle, calculé sur les dates — pas sur une phrase figée.
    final now = DateTime.now();
    final status = mc.statusAt(now);
    final days = mc.daysLeftAt(now);
    final (stateText, stateColor) = switch (status) {
      0 => (
          days == null
              ? l.t("contentOngoing")
              : "${l.t("contentOngoing")} · ${l.t("contentEndsIn")} $days ${l.t("contentDays")}",
          const Color(0xFF8BE28B)
        ),
      -1 => (
          days == null
              ? l.t("contentUpcoming")
              : "${l.t("contentUpcoming")} · $days ${l.t("contentDays")}",
          const Color(0xFFF2C14E)
        ),
      1 => (l.t("contentEnded"), const Color(0xFFF2C14E)),
      _ => ("", Colors.transparent),
    };

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            cs.primary.withValues(alpha: 0.10),
            cs.tertiary.withValues(alpha: 0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: cs.primary.withValues(alpha: 0.30)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.event, size: 15, color: cs.primary),
              const SizedBox(width: 8),
              Text(
                "${l.t("contentCurrent")} · $modeLabel".toUpperCase(),
                style: TextStyle(
                  fontSize: 10.5,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w800,
                  color: cs.primary,
                ),
              ),
              const Spacer(),
              Text(
                "${mc.cycle} · ${l.t("contentUpdated")} ${content.updated}",
                style: TextStyle(
                  fontSize: 10.5,
                  color: Colors.white.withValues(alpha: 0.45),
                ),
              ),
            ],
          ),
          if (stateText.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
              decoration: BoxDecoration(
                color: stateColor.withValues(alpha: 0.14),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                stateText,
                style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: stateColor),
              ),
            ),
          ],
          const SizedBox(height: 10),
          Text(
            mc.headline,
            style: const TextStyle(
                fontSize: 13, fontWeight: FontWeight.w700, height: 1.45),
          ),
          if (mc.detail.isNotEmpty) ...[
            const SizedBox(height: 5),
            Text(
              mc.detail,
              style: TextStyle(
                fontSize: 12,
                height: 1.45,
                color: Colors.white.withValues(alpha: 0.65),
              ),
            ),
          ],
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.tips_and_updates_outlined,
                  size: 15, color: cs.secondary),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  mc.strategy,
                  style: TextStyle(
                    fontSize: 12,
                    height: 1.5,
                    color: Colors.white.withValues(alpha: 0.7),
                  ),
                ),
              ),
            ],
          ),
          if (mc.source.isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.verified_outlined,
                    size: 13, color: Colors.white.withValues(alpha: 0.35)),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    mc.source,
                    style: TextStyle(
                      fontSize: 10.5,
                      color: Colors.white.withValues(alpha: 0.38),
                    ),
                  ),
                ),
              ],
            ),
          ],
          if (bestTeamName != null) ...[
            const SizedBox(height: 10),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
              decoration: BoxDecoration(
                color: cs.primary.withValues(alpha: 0.14),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                "★ ${l.t("contentBestForYou")} $bestTeamName",
                style: const TextStyle(
                    fontSize: 12, fontWeight: FontWeight.w700),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
