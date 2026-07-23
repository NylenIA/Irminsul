"use server";

import {
  buildDirectHitPreview,
  type DirectHitPreviewRequest,
  type DirectHitPreviewResult,
} from "@irminsul/engine-client";
import { SidecarEngineClient } from "@irminsul/engine-client/sidecar";
import { engineOptions } from "@/server/engine";

/**
 * Aperçu de coup direct — Server Action mince : validation/orchestration dans
 * `@irminsul/engine-client` (pur, testé). Par DÉFAUT le résultat est recalculé par le
 * VRAI moteur Python (engine_stdio.py en dev, binaire gelé en desktop) ; parité TS↔Python
 * prouvée par goldens. IRMINSUL_ENGINE=local force le port TS (opt-out, ex. environnement
 * sans Python). En cas d'échec sidecar : repli TS documenté — la provenance (`engine`)
 * reflète toujours le moteur réellement utilisé (jamais de faux "python-sidecar").
 */
export async function previewDirectHitAction(
  request: DirectHitPreviewRequest,
): Promise<DirectHitPreviewResult> {
  const preview = buildDirectHitPreview(request);
  if (!preview.ok || process.env["IRMINSUL_ENGINE"] === "local") return preview;

  // Chemin sidecar (défaut) : mêmes paramètres (déjà validés/convertis), moteur réel.
  try {
    const sidecar = new SidecarEngineClient(engineOptions());
    const p = preview.preview.parameters;
    const outcome = await sidecar.calculateDirectHit({
      scaling: p["scaling"]!,
      scalingStat: p["scalingStat"]!,
      critRate: p["critRate"],
      critDamage: p["critDamage"],
      damageBonus: p["damageBonus"],
      enemyLevel: p["enemyLevel"],
      enemyResistance: p["enemyResistance"],
      attackerLevel: p["attackerLevel"],
      amplifyingReactionMultiplier: p["amplifyingReactionMultiplier"],
      // Réactions additives : le bonus fait partie de la BASE du coup (sinon perdu).
      flatBaseDamage: p["flatBaseDamage"],
    });
    return { ok: true, preview: { ...preview.preview, outcome } };
  } catch {
    // Repli documenté : moteur TS local (parité goldens) ; provenance reste "ts-port".
    return preview;
  }
}
