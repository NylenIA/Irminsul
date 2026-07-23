"use server";

import { statSync } from "node:fs";
import { callEngine } from "@/server/engine";
import {
  checkSchemaDrift,
  prisma,
  EXPECTED_MIGRATIONS,
  type SchemaDriftStatus,
} from "@irminsul/data-access";

/**
 * Diagnostic SANITIZÉ : provenance réelle du moteur (dispatcher canonique) + état app/base.
 * Aucun secret/nonce/token ; les chemins locaux sont masqués (répertoire utilisateur → ~).
 */
export interface DiagnosticReport {
  app: { version: string; mode: "desktop" | "web"; nodeVersion: string };
  engine:
    | { ok: true; ipcContract: string; methods: string[]; frozen: boolean; gitCommit: string | null; binarySha256: string | null; python: string }
    | { ok: false; error: string };
  database: {
    url: string;
    sizeBytes: number | null;
    modifiedAt: string | null;
    schema: { status: SchemaDriftStatus; detail: string };
  };
  security: { loopbackOnly: true; bundleSigned: false; smartScreenWarning: true };
}

function maskPath(p: string): string {
  // Audit L2 : redaction GÉNÉRALISÉE — tout chemin absolu (lecteur ou UNC) est réduit à
  // ~…/<basename>. Aucun nom de compte ni layout local ne fuit à l'écran ou dans la copie.
  return p
    .replace(/(?:[A-Za-z]:|\\\\[^\\/\s"']+)[\\/][^\s"']*[\\/]([^\\/\s"']+)/g, "~…/$1")
    .replace(/(?:[A-Za-z]:|\\\\[^\\/\s"']+)[\\/][^\s"']+/g, "~…");
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

  // Dérive de schéma : détecte une base %APPDATA% en retard sur les migrations de
  // cette version (cas d'une MAJ desktop) pour l'afficher honnêtement plutôt que
  // de laisser l'app échouer plus loin. Ne modifie/applique RIEN.
  let schema: { status: SchemaDriftStatus; detail: string };
  try {
    const drift = await checkSchemaDrift(prisma, EXPECTED_MIGRATIONS);
    schema = { status: drift.status, detail: drift.detail };
  } catch {
    schema = { status: "unknown", detail: "Vérification du schéma impossible (base injoignable)." };
  }

  return {
    app: { version: "0.1.0", mode: isDesktop ? "desktop" : "web", nodeVersion: process.version },
    engine,
    database: { url: maskPath(dbUrl), sizeBytes, modifiedAt, schema },
    security: { loopbackOnly: true, bundleSigned: false, smartScreenWarning: true },
  };
}
