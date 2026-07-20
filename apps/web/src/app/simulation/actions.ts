"use server";

import { runSidecar } from "@irminsul/engine-client/sidecar";
import { engineOptions } from "@/server/engine";

export interface GcsimRunResult {
  ok: boolean;
  returncode: number;
  parsed: { damage?: number; duration?: number; dps: number; partial?: boolean } | null;
  output: string;
}

export type GcsimActionResult =
  | { ok: true; result: GcsimRunResult }
  | { ok: false; kind: "validation_error" | "engine_error"; message: string };

/**
 * Simulation gcsim RÉELLE (binaire local) depuis un contenu de config.
 * Timeout étendu : une simulation peut durer bien plus qu'un appel moteur
 * classique. Jamais de DPS inventé : erreur typée si binaire/config absents.
 */
export async function runGcsimAction(config: string): Promise<GcsimActionResult> {
  if (!config || config.trim().length === 0) {
    return { ok: false, kind: "validation_error", message: "Configuration vide." };
  }
  try {
    const raw = await runSidecar(
      { ...engineOptions(), timeoutMs: 180000 },
      { method: "run_gcsim", params: { config } },
    );
    return { ok: true, result: raw as unknown as GcsimRunResult };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Erreur moteur inconnue.";
    return { ok: false, kind: "engine_error", message };
  }
}
