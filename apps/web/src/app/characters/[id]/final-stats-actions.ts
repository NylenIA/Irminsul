"use server";

import path from "node:path";
import { normalizeFinalStats, type FinalStatsResult } from "@irminsul/engine-client";
import { runSidecar, SidecarError } from "@irminsul/engine-client/sidecar";

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
  const repoRoot = path.join(process.cwd(), "..", "..");
  try {
    const raw = await runSidecar(
      {
        pythonPath:
          process.env["IRMINSUL_PYTHON"] ?? path.join(repoRoot, ".venv", "Scripts", "python.exe"),
        scriptPath: path.join(repoRoot, "scripts", "engine_stdio.py"),
        timeoutMs: 12000,
      },
      { method: "character_final_stats", params: { key: key.trim() } },
    );
    return normalizeFinalStats(raw as Parameters<typeof normalizeFinalStats>[0]);
  } catch (error) {
    const message = error instanceof SidecarError ? error.message : "Erreur moteur inconnue.";
    return { ok: false, kind: "engine_error", message };
  }
}
