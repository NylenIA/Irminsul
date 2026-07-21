"use server";

import { runSidecar } from "@irminsul/engine-client/sidecar";
import { getTeamRepository } from "@irminsul/data-access";
import { teamToGcsimSkeleton, type GcsimBuildInput } from "@irminsul/engine-client";
import { engineOptions } from "@/server/engine";
import { loadPlayerBuildAction } from "@/app/team-lab/build-actions";

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

export type GcsimSkeletonActionResult =
  | { ok: true; skeleton: string; enriched: number; total: number }
  | { ok: false; message: string };

/**
 * Squelette gcsim d'une équipe sauvegardée, ENRICHI des builds réels (scan GOOD)
 * quand le personnage est scanné. La génération (fonction pure testée) reste
 * dans engine-client ; ici on orchestre le chargement des builds côté serveur.
 * Aucune stat inventée : les substats restent TODO (non fournis par le scan).
 */
export async function buildGcsimSkeletonAction(teamId: string): Promise<GcsimSkeletonActionResult> {
  let team;
  try {
    team = await getTeamRepository().getById(teamId);
  } catch {
    return { ok: false, message: "Base locale indisponible." };
  }
  if (!team) return { ok: false, message: "Équipe introuvable." };

  const members = team.members.map((m) => ({ character: m.character, slot: m.slot }));
  const builds: Record<string, GcsimBuildInput> = {};
  let enriched = 0;
  for (const m of members) {
    const res = await loadPlayerBuildAction(m.character);
    if (res.ok) {
      const b = res.build;
      builds[m.character] = {
        level: b.level,
        ascension: b.ascension,
        constellation: b.constellation,
        talents: b.talents,
        weapon: b.weapon,
        artifactSets: b.artifactSets,
      };
      enriched += 1;
    }
  }

  try {
    const skeleton = teamToGcsimSkeleton(members, { builds });
    return { ok: true, skeleton, enriched, total: members.length };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Génération impossible." };
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
