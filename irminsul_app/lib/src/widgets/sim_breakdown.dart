import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../data/characters_repository.dart";
import "../i18n/strings.dart";
import "../services/gcsim_service.dart";
import "../state/providers.dart";
import "../theme.dart";
import "char_icon.dart";

/// Détail par personnage d'une simulation : barres de DPS (couleur d'élément)
/// + temps de terrain. Pour COMPRENDRE la méta, pas juste lire un chiffre.
class SimBreakdown extends ConsumerWidget {
  final SimResult result;
  const SimBreakdown({super.key, required this.result});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = L(ref.watch(localeProvider));
    final chars = ref.watch(charactersFullProvider).maybeWhen(
          data: (list) => list,
          orElse: () => const <CharacterFull>[],
        );
    if (result.perChar.isEmpty) return const SizedBox.shrink();

    CharacterFull? find(String gcsimName) {
      for (final c in chars) {
        if (GcsimService.gcsimName(c.good) == gcsimName) return c;
      }
      return null;
    }

    final maxDps = result.perChar
        .map((c) => c.dps)
        .fold<double>(1, (a, b) => a > b ? a : b);
    final energy = result.energyIssues;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ---- alerte n°1 des DPS trop bas : ultimes impossibles à charger ----
        if (energy.isNotEmpty)
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(11),
            decoration: BoxDecoration(
              color: const Color(0xFFF2C14E).withValues(alpha: 0.10),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                  color: const Color(0xFFF2C14E).withValues(alpha: 0.35)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "⚡ ${l.t("simEnergyTitle")}",
                  style: const TextStyle(
                      fontSize: 12.5, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 5),
                for (final e in energy)
                  Text(
                    "• ${find(e.gcsimName)?.name ?? e.gcsimName} — "
                    "${l.t("simEnergyBurstFail")} ${e.count.round()}×",
                    style: const TextStyle(fontSize: 12, height: 1.45),
                  ),
                const SizedBox(height: 5),
                Text(
                  l.t("simEnergyAdvice"),
                  style: TextStyle(
                    fontSize: 11.5,
                    height: 1.45,
                    color: Colors.white.withValues(alpha: 0.65),
                  ),
                ),
              ],
            ),
          ),
        Padding(
          padding: const EdgeInsets.only(bottom: 8, top: 4),
          child: Text(
            l.t("simBreakdown").toUpperCase(),
            style: TextStyle(
              fontSize: 10.5,
              letterSpacing: 1.2,
              fontWeight: FontWeight.w700,
              color: Colors.white.withValues(alpha: 0.5),
            ),
          ),
        ),
        for (final c in result.perChar)
          Padding(
            padding: const EdgeInsets.only(bottom: 7),
            child: Row(
              children: [
                if (find(c.gcsimName) != null)
                  CharIcon(
                    name: find(c.gcsimName)!.name,
                    icon: find(c.gcsimName)!.icon,
                    element: find(c.gcsimName)!.element,
                    size: 26,
                    showName: false,
                  )
                else
                  SizedBox(
                    width: 26,
                    child: Text(
                      c.gcsimName.substring(0, 2).toUpperCase(),
                      style: const TextStyle(
                          fontSize: 10, fontWeight: FontWeight.w800),
                    ),
                  ),
                const SizedBox(width: 10),
                SizedBox(
                  width: 92,
                  child: Text(
                    find(c.gcsimName)?.name ?? c.gcsimName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 11.5),
                  ),
                ),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(5),
                    child: LinearProgressIndicator(
                      value: (c.dps / maxDps).clamp(0.02, 1),
                      minHeight: 8,
                      backgroundColor: Colors.white.withValues(alpha: 0.06),
                      valueColor: AlwaysStoppedAnimation(
                        elementColor(find(c.gcsimName)?.element ?? "none")
                            .withValues(alpha: 0.85),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                SizedBox(
                  width: 118,
                  child: Text(
                    "${c.dps.round()} · ${c.fieldSeconds.toStringAsFixed(0)} s ${l.t("simFieldTime")}",
                    textAlign: TextAlign.right,
                    style: TextStyle(
                      fontSize: 10.5,
                      color: Colors.white.withValues(alpha: 0.55),
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
