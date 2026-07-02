"use server";

import {
  buildDirectHitPreview,
  type DirectHitPreviewRequest,
  type DirectHitPreviewResult,
} from "@irminsul/engine-client";

/**
 * Aperçu de coup direct — Server Action mince : toute la validation/orchestration vit dans
 * `@irminsul/engine-client` (pur, testé). Le moteur reste côté serveur ; l'UI ne reçoit
 * qu'un DTO sérialisable (résultat + provenance + hypothèses + version de contrat).
 */
export async function previewDirectHitAction(
  request: DirectHitPreviewRequest,
): Promise<DirectHitPreviewResult> {
  return buildDirectHitPreview(request);
}
