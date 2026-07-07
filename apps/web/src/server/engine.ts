/**
 * Résolution UNIFIÉE du moteur pour les Server Actions.
 * - Desktop installé : `IRMINSUL_SIDECAR_EXE` (posée par Tauri) → binaire gelé canonique.
 * - Dev/web : Python du repo + pont `scripts/engine_stdio.py` (même table canonique).
 * Les deux chemins exposent les MÊMES méthodes (dispatcher canonique, testé par parité).
 */
import path from "node:path";
import { runSidecar, type SidecarOptions } from "@irminsul/engine-client/sidecar";

const REPO_ROOT = path.join(process.cwd(), "..", "..");

export function engineOptions(): SidecarOptions {
  const frozen = process.env["IRMINSUL_SIDECAR_EXE"];
  if (frozen) {
    return { frozenExePath: frozen, timeoutMs: 20000 };
  }
  return {
    pythonPath:
      process.env["IRMINSUL_PYTHON"] ?? path.join(REPO_ROOT, ".venv", "Scripts", "python.exe"),
    scriptPath: path.join(REPO_ROOT, "scripts", "engine_stdio.py"),
    timeoutMs: 15000,
  };
}

/** Appel moteur générique (méthode du dispatcher canonique). */
export async function callEngine(
  method: string,
  params: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  return runSidecar(engineOptions(), { method, params });
}
