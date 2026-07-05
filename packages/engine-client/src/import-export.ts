/**
 * Import/Export versionné `irminsul-export/1.0` — moteur PUR (validation, migration, diff, checksum).
 * Aucune I/O ici (le transport — download navigateur ou dialog Tauri — est branché par l'appelant).
 * Aucun secret/token/donnée machine exporté. Import sans exécution de contenu (parse strict).
 */
export const EXPORT_FORMAT_VERSION = "irminsul-export/1.0";
const SUPPORTED_VERSIONS = new Set(["irminsul-export/1.0"]);
export const MAX_IMPORT_BYTES = 2 * 1024 * 1024; // 2 Mo : borne anti-DoS

export interface ExportableTeam {
  name: string;
  members: { character: string; role: string | null; slot: number }[];
}

export interface ExportData {
  teams: ExportableTeam[];
}

export interface ExportFile {
  formatVersion: string;
  appVersion: string;
  exportedAt: string;
  data: ExportData;
  /** Checksum d'intégrité (non cryptographique) sur le JSON canonique de `data`. */
  checksum: string;
}

/** Hash déterministe FNV-1a 32 bits (intégrité, pas sécurité) sur une chaîne. */
export function checksumOf(data: ExportData): string {
  const canonical = canonicalJson(data);
  let h = 0x811c9dc5;
  for (let i = 0; i < canonical.length; i++) {
    h ^= canonical.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16).padStart(8, "0");
}

/** JSON canonique : clés triées, pour un checksum stable indépendant de l'ordre. */
function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") {
    const keys = Object.keys(value as Record<string, unknown>).sort();
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson((value as Record<string, unknown>)[k])}`).join(",")}}`;
  }
  return JSON.stringify(value ?? null);
}

export function buildExport(teams: ExportableTeam[], appVersion: string, now = new Date()): ExportFile {
  const data: ExportData = {
    // Ordre déterministe (nom) pour un export lisible et reproductible.
    teams: teams
      .map((t) => ({
        name: t.name,
        members: t.members.slice().sort((a, b) => a.slot - b.slot),
      }))
      .sort((a, b) => a.name.localeCompare(b.name)),
  };
  return {
    formatVersion: EXPORT_FORMAT_VERSION,
    appVersion,
    exportedAt: now.toISOString(),
    data,
    checksum: checksumOf(data),
  };
}

export type ImportValidation =
  | { ok: true; file: ExportFile; migrated: boolean }
  | { ok: false; kind: "too_large" | "invalid_json" | "invalid_schema" | "unsupported_version" | "checksum_mismatch"; issues: string[] };

function isExportableTeam(t: unknown): t is ExportableTeam {
  if (!t || typeof t !== "object") return false;
  const o = t as Record<string, unknown>;
  if (typeof o["name"] !== "string" || !Array.isArray(o["members"])) return false;
  return o["members"].every((m) => {
    if (!m || typeof m !== "object") return false;
    const mm = m as Record<string, unknown>;
    return typeof mm["character"] === "string"
      && (mm["role"] === null || typeof mm["role"] === "string")
      && typeof mm["slot"] === "number" && Number.isInteger(mm["slot"]);
  });
}

/** Valide un texte importé : taille, JSON, schéma, version (migration si possible), checksum. */
export function validateImport(raw: string): ImportValidation {
  if (raw.length > MAX_IMPORT_BYTES) {
    return { ok: false, kind: "too_large", issues: [`Fichier trop volumineux (> ${MAX_IMPORT_BYTES} octets).`] };
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw); // parse strict — aucune exécution de contenu
  } catch {
    return { ok: false, kind: "invalid_json", issues: ["JSON invalide."] };
  }
  if (!parsed || typeof parsed !== "object") {
    return { ok: false, kind: "invalid_schema", issues: ["Racine du fichier invalide."] };
  }
  const obj = parsed as Record<string, unknown>;
  const version = obj["formatVersion"];
  if (typeof version !== "string") {
    return { ok: false, kind: "invalid_schema", issues: ["`formatVersion` manquant."] };
  }

  let migrated = false;
  let normalized = obj;
  // Migration de versions plus anciennes (aucune connue avant 1.0 ; point d'extension prêt).
  if (!SUPPORTED_VERSIONS.has(version)) {
    const m = tryMigrate(version, obj);
    if (!m) {
      return { ok: false, kind: "unsupported_version", issues: [`Version « ${version} » non prise en charge (attendu ${EXPORT_FORMAT_VERSION}).`] };
    }
    normalized = m;
    migrated = true;
  }

  const data = normalized["data"];
  if (!data || typeof data !== "object" || !Array.isArray((data as Record<string, unknown>)["teams"])) {
    return { ok: false, kind: "invalid_schema", issues: ["`data.teams` manquant ou invalide."] };
  }
  const teams = (data as { teams: unknown[] }).teams;
  if (!teams.every(isExportableTeam)) {
    return { ok: false, kind: "invalid_schema", issues: ["Une ou plusieurs équipes ont un format invalide."] };
  }

  const file: ExportFile = {
    formatVersion: EXPORT_FORMAT_VERSION,
    appVersion: typeof normalized["appVersion"] === "string" ? (normalized["appVersion"] as string) : "inconnue",
    exportedAt: typeof normalized["exportedAt"] === "string" ? (normalized["exportedAt"] as string) : new Date(0).toISOString(),
    data: { teams: teams as ExportableTeam[] },
    checksum: typeof normalized["checksum"] === "string" ? (normalized["checksum"] as string) : "",
  };
  // Vérif checksum si présent (fichiers 1.0 en ont un). Un mismatch = corruption → refus.
  if (file.checksum && file.checksum !== checksumOf(file.data)) {
    return { ok: false, kind: "checksum_mismatch", issues: ["Checksum invalide : fichier corrompu ou modifié."] };
  }
  return { ok: true, file, migrated };
}

/** Point d'extension de migration. Retourne un objet normalisé 1.0, ou null si non migrable. */
function tryMigrate(_version: string, _obj: Record<string, unknown>): Record<string, unknown> | null {
  // Aucune version < 1.0 n'existe encore. Exemple futur :
  // if (_version === "irminsul-export/0.9") return { ..._obj, formatVersion: EXPORT_FORMAT_VERSION };
  return null;
}

export interface ImportPlanEntry {
  name: string;
  status: "created" | "updated" | "conflict" | "identical";
  detail: string;
}
export interface ImportPlan {
  entries: ImportPlanEntry[];
  created: number;
  updated: number;
  conflicts: number;
  identical: number;
  total: number;
}

/** Aperçu déterministe AVANT écriture : que fera l'import face aux équipes existantes ? */
export function planImport(file: ExportFile, existingTeamNames: string[]): ImportPlan {
  const existing = new Set(existingTeamNames);
  const seen = new Set<string>();
  const entries: ImportPlanEntry[] = [];
  for (const t of file.data.teams) {
    if (seen.has(t.name)) {
      entries.push({ name: t.name, status: "conflict", detail: "Doublon dans le fichier d'import (ignoré)." });
      continue;
    }
    seen.add(t.name);
    if (existing.has(t.name)) {
      entries.push({ name: t.name, status: "updated", detail: "Une équipe du même nom existe — sera remplacée (sauvegarde conservée)." });
    } else {
      entries.push({ name: t.name, status: "created", detail: "Nouvelle équipe." });
    }
  }
  return {
    entries,
    created: entries.filter((e) => e.status === "created").length,
    updated: entries.filter((e) => e.status === "updated").length,
    conflicts: entries.filter((e) => e.status === "conflict").length,
    identical: entries.filter((e) => e.status === "identical").length,
    total: entries.length,
  };
}
