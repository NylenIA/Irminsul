"use server";

import {
  buildExport,
  planImport,
  validateImport,
  type ExportFile,
  type ImportPlan,
} from "@irminsul/engine-client";
import { getTeamRepository } from "@irminsul/data-access";

const APP_VERSION = "0.1.0";

export interface ExportResponse {
  fileName: string;
  content: string;
  teamCount: number;
}

/** Export des équipes sauvegardées (données utilisateur) au format versionné + checksum. */
export async function exportTeamsAction(): Promise<ExportResponse> {
  const teams = await getTeamRepository().list();
  const file = buildExport(
    teams.map((t) => ({ name: t.name, members: t.members })),
    APP_VERSION,
  );
  const stamp = new Date().toISOString().slice(0, 10);
  return {
    fileName: `irminsul-export-${stamp}.json`,
    content: JSON.stringify(file, null, 2),
    teamCount: file.data.teams.length,
  };
}

export type PreviewResponse =
  | { ok: true; plan: ImportPlan; migrated: boolean; appVersion: string; exportedAt: string; teamCount: number }
  | { ok: false; message: string };

/** Aperçu AVANT écriture : valide le fichier et montre created/updated/conflicts. */
export async function previewImportAction(raw: string): Promise<PreviewResponse> {
  const v = validateImport(raw);
  if (!v.ok) return { ok: false, message: v.issues.join(" ") };
  const existing = await getTeamRepository().list();
  const plan = planImport(v.file, existing.map((t) => t.name));
  return {
    ok: true,
    plan,
    migrated: v.migrated,
    appVersion: v.file.appVersion,
    exportedAt: v.file.exportedAt,
    teamCount: v.file.data.teams.length,
  };
}

export type ApplyResponse =
  | { ok: true; created: number; updated: number }
  | { ok: false; message: string };

/** Applique l'import de façon TRANSACTIONNELLE (tout ou rien) après re-validation serveur. */
export async function applyImportAction(raw: string): Promise<ApplyResponse> {
  const v = validateImport(raw);
  if (!v.ok) return { ok: false, message: v.issues.join(" ") };
  const file: ExportFile = v.file;
  try {
    const result = await getTeamRepository().importTeams(
      file.data.teams.map((t) => ({ name: t.name, members: t.members })),
    );
    return { ok: true, created: result.created, updated: result.updated };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Import impossible.";
    return { ok: false, message };
  }
}
