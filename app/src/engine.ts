/** Couche typée vers le moteur Python via commandes Tauri (cf. src-tauri/lib.rs).
 * Le moteur renvoie du JSON pur ; ici on le type et on gère les états réels. */
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";

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

export interface RosterCharacter {
  key: string;
  level: number | null;
  ascension: number | null;
  constellation: number | null;
  talents: { auto?: number; skill?: number; burst?: number };
  weapon: { key: string; level: number | null; refinement: number | null } | null;
  artifacts: number;
  dominant_set: string | null;
}
export interface RosterWeapon {
  key: string;
  level: number | null;
  refinement: number | null;
  location: string | null;
}
export interface RosterSet {
  setKey: string;
  total: number;
  equipped: number;
}
export interface Roster {
  counts: AccountCounts;
  characters: RosterCharacter[];
  weapons: RosterWeapon[];
  artifact_sets: RosterSet[];
}
export type RosterResponse = { status: "ok"; roster: Roster } | { status: "empty" };

export const getProfile = (): Promise<ProfileResponse> => call<ProfileResponse>("account_profile");
export const getRoster = (): Promise<RosterResponse> => call<RosterResponse>("account_roster");
export const importGood = (path: string): Promise<ImportResponse> =>
  call<ImportResponse>("account_import_good", { path });

export interface DirectHit {
  raw_base: number;
  non_crit: number;
  crit: number;
  expected: number;
  defense_multiplier: number;
  resistance_multiplier: number;
  expected_crit_multiplier: number;
}
export interface MechanicSource {
  name: string;
  type: string;
  url?: string;
}
export interface MechanicDetail {
  id: string;
  status: string;
  confidence: string;
  sources: MechanicSource[];
  verified_at?: string | null;
}
export interface QuickCalcResult {
  status: "ok";
  result: DirectHit;
  amplifying: { amplifying_multiplier: number; em_bonus: number } | null;
  additive: { base_bonus_damage: number; em_bonus: number; base_multiplier: number } | null;
  transformative:
    | { reaction: string; damage: number; base_multiplier: number; em_bonus: number }
    | null;
  mechanics_used: string[];
  mechanics_detail: MechanicDetail[];
  registry_version: string;
}
export const quickCalc = (params: Record<string, number | string>): Promise<QuickCalcResult> =>
  call<QuickCalcResult>("quick_calc", { params });

export interface ArtifactStats {
  totals: Record<string, number>;
  uncomputed_main: Array<{
    set: string;
    slot: string;
    rarity: number;
    level: number;
    mainStatKey: string;
    reason: string;
  }>;
  anomalies?: Array<{ set: string; slot: string; key: string; value: unknown; reason: string }>;
}
export interface BaseStatsProvenance {
  source?: string;
  source_commit?: string;
  source_commit_date?: string;
  formula?: string;
  confidence?: string;
}
export interface BaseStats {
  supported: boolean;
  reason?: string;
  hp?: number;
  atk?: number;
  def?: number;
  crit_rate_?: number;
  crit_dmg_?: number;
  ascension_stat_key?: string;
  ascension_stat_value?: number;
  level?: number;
  ascension?: number;
  provenance?: BaseStatsProvenance;
  confidence?: string;
}
export interface FinalStatCell {
  value: number | null;
  complete: boolean;
  missing: string[];
}
export interface WeaponBaseStats {
  supported: boolean;
  reason?: string;
  key?: string | null;
  base_atk?: number;
  secondary_stat_key?: string | null;
  secondary_stat_value?: number;
  level?: number;
  ascension?: number;
  max_level?: number;
  max_ascension?: number;
  provenance?: BaseStatsProvenance;
  confidence?: string;
}
export interface FinalStats {
  complete: boolean;
  note: string;
  weapon: {
    supported: boolean;
    valid: boolean;
    key: string | null;
    base_atk: number | null;
    secondary_stat_key: string | null;
    secondary_stat_value: number | null;
  };
  ascension_stat_applied: { key: string; value: number };
  artifact_main_incomplete: string[];
  hp: FinalStatCell;
  atk: FinalStatCell;
  def: FinalStatCell;
  crit_rate_: FinalStatCell;
  crit_dmg_: FinalStatCell;
  eleMas: FinalStatCell;
  enerRech_: FinalStatCell;
  dmg_bonus: Record<string, number>;
}
export interface CharacterInfo {
  key: string;
  level: number | null;
  ascension: number | null;
  constellation: number | null;
  talents: { auto?: number; skill?: number; burst?: number };
  weapon: { key: string; level: number | null; refinement: number | null } | null;
  artifacts: Array<{ setKey: string; slotKey: string; rarity: number; level: number; mainStatKey: string }>;
  artifact_stats: ArtifactStats;
  base_stats: BaseStats;
  weapon_base_stats: WeaponBaseStats;
  final_stats: FinalStats | null;
  unsupported: Array<{ item: string; reason: string }>;
  provenance: { snapshot_date: string | null; source: string | null; sha256: string | null; good_version: number | null };
}
export type CharactersResponse = { status: "ok"; characters: string[] } | { status: "empty" };
export type CharacterStatsResponse =
  | { status: "ok"; character: CharacterInfo }
  | { status: "empty" }
  | { status: "not_found"; key: string };

export const getCharacters = (): Promise<CharactersResponse> =>
  call<CharactersResponse>("account_characters");
export const getCharacterStats = (key: string): Promise<CharacterStatsResponse> =>
  call<CharacterStatsResponse>("character_stats", { key });

/** Sélecteur de fichier natif (plugin dialog Tauri) pour choisir l'export GOOD. */
export async function pickGoodFile(): Promise<string | null> {
  const selected = await open({
    multiple: false,
    directory: false,
    filters: [{ name: "Export GOOD", extensions: ["json"] }],
  });
  return typeof selected === "string" ? selected : null;
}
