"use server";

import { normalizeFinalStats, type FinalStatsResult } from "@irminsul/engine-client";
import { SidecarError } from "@irminsul/engine-client/sidecar";
import { callEngine } from "@/server/engine";

/**
 * Stats finales d'un personnage via le VRAI moteur Python (`charstats.character_payload`)
 * exécuté par le sidecar borné. Serveur uniquement ; l'adapter `normalizeFinalStats` (pur,
 * testé) produit un DTO sûr (provenance curée, aucune stat inventée). En cas d'échec sidecar,
 * erreur typée — pas de repli TS possible (le calcul de stats finales n'existe qu'en Python).
 */
export async function loadFinalStatsAction(key: string): Promise<FinalStatsResult> {
  if (!key || !key.trim()) {
    return { ok: false, kind: "not_found", message: "Nom de personnage manquant." };
  }
  try {
    const raw = await callEngine("character_final_stats", { key: key.trim() });
    return normalizeFinalStats(raw as Parameters<typeof normalizeFinalStats>[0]);
  } catch (error) {
    const message = error instanceof SidecarError ? error.message : "Erreur moteur inconnue.";
    return { ok: false, kind: "engine_error", message };
  }
}
