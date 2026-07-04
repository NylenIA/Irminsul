"use server";

import path from "node:path";
import {
  normalizeRotation,
  validateRotation,
  type RotationAction,
  type RotationResult,
} from "@irminsul/engine-client";
import { runSidecar, SidecarError } from "@irminsul/engine-client/sidecar";

export type RotationActionResponse =
  | { ok: true; result: RotationResult }
  | { ok: false; kind: "validation_error"; issues: string[] }
  | { ok: false; kind: "engine_error"; message: string };

/**
 * Calcule une rotation via le moteur Python (coefficients + stats réels). Validation TS PURE
 * d'abord (défense en profondeur), puis sidecar. Aucun DPS fabriqué ; erreurs typées.
 */
export async function calculateRotationAction(
  team: string[],
  actions: RotationAction[],
): Promise<RotationActionResponse> {
  const issues = validateRotation(team, actions);
  if (issues.length > 0) return { ok: false, kind: "validation_error", issues };

  const repoRoot = path.join(process.cwd(), "..", "..");
  try {
    const raw = await runSidecar(
      {
        pythonPath:
          process.env["IRMINSUL_PYTHON"] ?? path.join(repoRoot, ".venv", "Scripts", "python.exe"),
        scriptPath: path.join(repoRoot, "scripts", "engine_stdio.py"),
        timeoutMs: 15000,
      },
      {
        method: "calculate_rotation",
        params: { team, actions },
      },
    );
    return { ok: true, result: normalizeRotation(raw as Parameters<typeof normalizeRotation>[0]) };
  } catch (error) {
    const message = error instanceof SidecarError ? error.message : "Erreur moteur inconnue.";
    return { ok: false, kind: "engine_error", message };
  }
}
