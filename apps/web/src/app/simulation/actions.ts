"use server";

import { runSidecar } from "@irminsul/engine-client/sidecar";
import { getTeamRepository } from "@irminsul/data-access";
import { engineOptions } from "@/server/engine";

export interface SimTeamOption {
  id: string;
  name: string;
  members: { character: string; slot: number }[];
}

/**
 * Équipes sauvegardées pour pré-remplir un squelette gcsim. Renvoie une liste
 * vide (jamais d'erreur bloquante) si la base locale est indisponible.
 */
export async function listTeamsForSimAction(): Promise<SimTeamOption[]> {
  try {
    const teams = await getTeamRepository().list();
    return teams.map((t) => ({
      id: t.id,
      name: t.name,
      members: t.members.map((m) => ({ character: m.character, slot: m.slot })),
    }));
  } catch {
    return [];
  }
}

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
