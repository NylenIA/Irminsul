/**
 * Import/Export versionné `irminsul-export/1.0` — moteur PUR (validation, migration, diff, checksum).
 * Aucune I/O ici (le transport — download navigateur ou dialog Tauri — est branché par l'appelant).
 * Aucun secret/token/donnée machine exporté. Import sans exécution de contenu (parse strict).
 */
export const EXPORT_FORMAT_VERSION = "irminsul-export/1.0";
const SUPPORTED_VERSIONS = new Set(["irminsul-export/1.0"]);
export const MAX_IMPORT_BYTES = 2 * 1024 * 1024; // 2 Mo : borne anti-DoS
// Bornes STRUCTURELLES (audit Codex M1) : un fichier < 2 Mo mais profond/large ne doit pas
// saturer CPU/stack. Alignées sur le repository (importTeams ≤ 500, équipe 1..4 membres).
export const MAX_TEAMS_PER_FILE = 500;
const MAX_MEMBERS_PER_TEAM = 4;
const MAX_NAME_LENGTH = 200;
const MAX_JSON_DEPTH = 30;

/** Scan linéaire de profondeur AVANT JSON.parse (pas de stack overflow sur JSON profond). */
function jsonDepthExceeds(raw: string, limit: number): boolean {
  let depth = 0;
  let inStr = false;
  let esc = false;
  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i];
    if (esc) { esc = false; continue; }
    if (ch === "\\") { if (inStr) esc = true; continue; }
    if (ch === '"') { inStr = !inStr; continue; }
    if (inStr) continue;
    if (ch === "{" || ch === "[") { depth++; if (depth > limit) return true; }
    else if (ch === "}" || ch === "]") depth--;
  }
  return false;
}

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
  // Bornes structurelles (audit M1) : nom borné, 1..4 membres.
  if (o["name"].trim().length === 0 || o["name"].length > MAX_NAME_LENGTH) return false;
  if (o["members"].length < 1 || o["members"].length > MAX_MEMBERS_PER_TEAM) return false;
  return o["members"].every((m) => {
    if (!m || typeof m !== "object") return false;
    const mm = m as Record<string, unknown>;
    return typeof mm["character"] === "string"
      && mm["character"].length > 0 && mm["character"].length <= MAX_NAME_LENGTH
      && (mm["role"] === null || typeof mm["role"] === "string")
      && typeof mm["slot"] === "number" && Number.isInteger(mm["slot"]);
  });
}

/**
 * Sanitization stricte (audit M1) : ne conserve QUE les clés whitelistées, noms trimés.
 * Tout champ inconnu est purgé — le checksum est ensuite vérifié sur la copie sanitizée
 * (un fichier « enrichi » de champs inconnus ⇒ checksum différent ⇒ rejet).
 */
function sanitizeTeams(teams: ExportableTeam[]): ExportableTeam[] {
  return teams.map((t) => ({
    name: t.name.trim(),
    members: t.members.map((m) => ({
      character: m.character.trim(),
      role: typeof m.role === "string" ? m.role : null,
      slot: m.slot,
    })),
  }));
}

/** Valide un texte importé : taille, profondeur, JSON, schéma strict, version, checksum REQUIS. */
export function validateImport(raw: string): ImportValidation {
  if (raw.length > MAX_IMPORT_BYTES) {
    return { ok: false, kind: "too_large", issues: [`Fichier trop volumineux (> ${MAX_IMPORT_BYTES} octets).`] };
  }
  // Audit M1 : profondeur bornée AVANT parse (linéaire, pas de récursion).
  if (jsonDepthExceeds(raw, MAX_JSON_DEPTH)) {
    return { ok: false, kind: "invalid_schema", issues: [`Structure trop profonde (> ${MAX_JSON_DEPTH} niveaux).`] };
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
  if (teams.length > MAX_TEAMS_PER_FILE) {
    return { ok: false, kind: "invalid_schema", issues: [`Trop d'équipes (> ${MAX_TEAMS_PER_FILE}).`] };
  }
  if (!teams.every(isExportableTeam)) {
    return { ok: false, kind: "invalid_schema", issues: ["Une ou plusieurs équipes ont un format invalide."] };
  }

  // Audit M2 : le checksum est REQUIS pour 1.0 (format exact 8 hex) — un fichier sans checksum
  // est refusé (plus de contournement par omission). NOTE de périmètre : FNV-1a = détection de
  // corruption, PAS un anti-tamper cryptographique (le fichier est une donnée locale de
  // l'utilisateur, revalidée structurellement à l'import ; aucun secret, aucune frontière de
  // confiance traversée). Documenté dans IMPORT_EXPORT contract.
  const rawChecksum = normalized["checksum"];
  if (typeof rawChecksum !== "string" || !/^[0-9a-f]{8}$/.test(rawChecksum)) {
    return { ok: false, kind: "invalid_schema", issues: ["Checksum manquant ou au format invalide (requis pour irminsul-export/1.0)."] };
  }

  // Audit M1 : sanitization stricte AVANT checksum — le parcours du checksum ne voit que la
  // structure whitelistée bornée (jamais l'objet brut).
  const sanitized = { teams: sanitizeTeams(teams as ExportableTeam[]) };
  if (rawChecksum !== checksumOf(sanitized)) {
    return { ok: false, kind: "checksum_mismatch", issues: ["Checksum invalide : fichier corrompu ou modifié."] };
  }

  const file: ExportFile = {
    formatVersion: EXPORT_FORMAT_VERSION,
    appVersion: typeof normalized["appVersion"] === "string" ? (normalized["appVersion"] as string) : "inconnue",
    exportedAt: typeof normalized["exportedAt"] === "string" ? (normalized["exportedAt"] as string) : new Date(0).toISOString(),
    data: sanitized,
    checksum: rawChecksum,
  };
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

/**
 * Aperçu déterministe AVANT écriture — MÊME politique que la persistance (audit L3) :
 * noms trimés (déjà sanitizés) et en cas de doublon interne, la DERNIÈRE occurrence gagne
 * (identique au `Map` de `importTeams`). L'aperçu et le résultat écrit coïncident toujours.
 */
export function planImport(file: ExportFile, existingTeamNames: string[]): ImportPlan {
  const existing = new Set(existingTeamNames.map((n) => n.trim()));
  const teams = file.data.teams;
  const lastIndexByName = new Map<string, number>();
  teams.forEach((t, i) => lastIndexByName.set(t.name, i));
  const entries: ImportPlanEntry[] = [];
  teams.forEach((t, i) => {
    if (lastIndexByName.get(t.name) !== i) {
      entries.push({ name: t.name, status: "conflict", detail: "Doublon dans le fichier — la dernière occurrence sera utilisée (celle-ci est ignorée)." });
      return;
    }
    if (existing.has(t.name)) {
      entries.push({ name: t.name, status: "updated", detail: "Une équipe du même nom existe — sera remplacée (sauvegarde conservée)." });
    } else {
      entries.push({ name: t.name, status: "created", detail: "Nouvelle équipe." });
    }
  });
  return {
    entries,
    created: entries.filter((e) => e.status === "created").length,
    updated: entries.filter((e) => e.status === "updated").length,
    conflicts: entries.filter((e) => e.status === "conflict").length,
    identical: entries.filter((e) => e.status === "identical").length,
    total: entries.length,
  };
}
