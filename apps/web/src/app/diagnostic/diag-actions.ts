"use server";

import { statSync } from "node:fs";
import { callEngine } from "@/server/engine";

/**
 * Diagnostic SANITIZÉ : provenance réelle du moteur (dispatcher canonique) + état app/base.
 * Aucun secret/nonce/token ; les chemins locaux sont masqués (répertoire utilisateur → ~).
 */
export interface DiagnosticReport {
  app: { version: string; mode: "desktop" | "web"; nodeVersion: string };
  engine:
    | { ok: true; ipcContract: string; methods: string[]; frozen: boolean; gitCommit: string | null; binarySha256: string | null; python: string }
    | { ok: false; error: string };
  database: { url: string; sizeBytes: number | null; modifiedAt: string | null };
  security: { loopbackOnly: true; bundleSigned: false; smartScreenWarning: true };
}

function maskPath(p: string): string {
  // Masquage raisonnable : le profil utilisateur devient ~ (pas de nom de compte exposé).
  return p.replace(/[A-Za-z]:[\\/](Users|Utilisateurs)[\\/][^\\/]+/i, "~");
}

export async function getDiagnosticAction(): Promise<DiagnosticReport> {
  const isDesktop = !!process.env["IRMINSUL_SIDECAR_EXE"];

  let engine: DiagnosticReport["engine"];
  try {
    const prov = await callEngine("engine_provenance", {});
    engine = {
      ok: true,
      ipcContract: String(prov["ipc_contract"] ?? "inconnu"),
      methods: Array.isArray(prov["methods"]) ? (prov["methods"] as string[]) : [],
      frozen: prov["frozen_binary"] === true,
      gitCommit: typeof prov["git_commit"] === "string" ? (prov["git_commit"] as string) : null,
      binarySha256: typeof prov["binary_sha256"] === "string" ? (prov["binary_sha256"] as string) : null,
      python: String(prov["python"] ?? "?"),
    };
  } catch (error) {
    engine = { ok: false, error: error instanceof Error ? maskPath(error.message) : "moteur injoignable" };
  }

  const dbUrl = process.env["DATABASE_URL"] ?? "(non configurée)";
  const dbPath = dbUrl.startsWith("file:") ? dbUrl.slice(5) : null;
  let sizeBytes: number | null = null;
  let modifiedAt: string | null = null;
  if (dbPath) {
    try {
      const st = statSync(dbPath);
      sizeBytes = st.size;
      modifiedAt = st.mtime.toISOString();
    } catch { /* base absente : affichée telle quelle */ }
  }

  return {
    app: { version: "0.1.0", mode: isDesktop ? "desktop" : "web", nodeVersion: process.version },
    engine,
    database: { url: maskPath(dbUrl), sizeBytes, modifiedAt },
    security: { loopbackOnly: true, bundleSigned: false, smartScreenWarning: true },
  };
}
