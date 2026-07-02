"use server";

import path from "node:path";
import {
  buildDirectHitPreview,
  type DirectHitPreviewRequest,
  type DirectHitPreviewResult,
} from "@irminsul/engine-client";
import { SidecarEngineClient } from "@irminsul/engine-client/sidecar";

/**
 * Aperçu de coup direct — Server Action mince : validation/orchestration dans
 * `@irminsul/engine-client` (pur, testé). Si IRMINSUL_ENGINE=sidecar, le résultat est
 * recalculé par le VRAI moteur Python (engine_stdio.py) ; en cas d'échec, repli silencieux
 * impossible : la provenance (`engine`) reflète toujours le moteur réellement utilisé.
 */
export async function previewDirectHitAction(
  request: DirectHitPreviewRequest,
): Promise<DirectHitPreviewResult> {
  const preview = buildDirectHitPreview(request);
  if (!preview.ok || process.env["IRMINSUL_ENGINE"] !== "sidecar") return preview;

  // Chemin sidecar : mêmes paramètres (déjà validés/convertis), moteur Python réel.
  try {
    const repoRoot = path.join(process.cwd(), "..", "..");
    const sidecar = new SidecarEngineClient({
      pythonPath: process.env["IRMINSUL_PYTHON"] ?? path.join(repoRoot, ".venv", "Scripts", "python.exe"),
      scriptPath: path.join(repoRoot, "scripts", "engine_stdio.py"),
      timeoutMs: 8000,
    });
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
    });
    return { ok: true, preview: { ...preview.preview, outcome } };
  } catch {
    // Repli documenté : moteur TS local (parité goldens) ; provenance reste "ts-port".
    return preview;
  }
}
