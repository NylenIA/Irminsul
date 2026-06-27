/** Couche typée vers le moteur Python via commandes Tauri (cf. src-tauri/lib.rs).
 * Le moteur renvoie du JSON pur ; ici on le type et on gère les états réels. */
import { invoke } from "@tauri-apps/api/core";

export interface AccountCounts {
  characters: number;
  weapons: number;
  artifacts: number;
  materials: number;
  equipped_weapons?: number;
  equipped_artifacts?: number;
  free_weapons?: number;
  free_artifacts?: number;
  unresolved_characters?: number;
}

export interface AccountProfile {
  snapshot_date: string | null;
  source: string | null;
  good_version: number | null;
  kamera_version: string | null;
  sha256: string | null;
  counts: AccountCounts;
  unresolved: string[];
  provenance_note?: string | null;
}

export type ProfileResponse =
  | { status: "ok"; profile: AccountProfile }
  | { status: "empty"; message?: string };

export interface Severities {
  INFO: number;
  WARNING: number;
  ERROR: number;
  BLOCKING: number;
}

export interface ImportSummary {
  sha256: string;
  snapshot: string;
  idempotent_skip: boolean;
  counts: AccountCounts;
  validation: Severities;
  unresolved: string[];
  duplicate_weapon_ids: boolean;
}

export type ImportResponse = { status: "ok"; import: ImportSummary } | { error: string };

/** Vrai si on tourne dans la coque Tauri (sinon : ouvert dans un navigateur). */
export function isDesktop(): boolean {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

async function call<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  const raw = await invoke<string>(cmd, args);
  return JSON.parse(raw) as T;
}

export const getProfile = (): Promise<ProfileResponse> => call<ProfileResponse>("account_profile");
export const importGood = (path: string): Promise<ImportResponse> =>
  call<ImportResponse>("account_import_good", { path });
