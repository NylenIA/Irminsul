/**
 * Adapter des stats finales d'un personnage (sortie du moteur Python `charstats.character_payload`
 * via le sidecar). Normalisation PURE et testable : convertit le payload brut en DTO typé, dérive
 * la confiance de la complétude RÉELLE (jamais gonflée), et n'invente aucune stat.
 * Contrat versionné : `final-stats/1.0`.
 */
export const FINAL_STATS_CONTRACT_VERSION = "final-stats/1.0";

/** Une cellule de stat : valeur + complétude + ce qui manque (affiché tel quel, jamais estimé). */
export interface FinalStatCell {
  value: number | null;
  complete: boolean;
  missing: string[];
}

export interface FinalStatsProvenance {
  snapshotDate?: string;
  source?: string;
  sha256?: string;
  goodVersion?: number;
}

export interface FinalCharacterStats {
  key: string;
  level?: number;
  ascension?: number;
  constellation?: number;
  /** true seulement si l'écran du jeu serait reproduit (arme supportée + aucune main-stat manquante). */
  complete: boolean;
  note: string;
  hp: FinalStatCell;
  atk: FinalStatCell;
  def: FinalStatCell;
  critRate: FinalStatCell;
  critDamage: FinalStatCell;
  elementalMastery: FinalStatCell;
  energyRecharge: FinalStatCell;
  damageBonuses: Record<string, number>;
  weapon: {
    supported: boolean;
    valid: boolean;
    key?: string;
    baseAtk?: number | null;
    secondaryStatKey?: string | null;
    secondaryStatValue?: number | null;
  };
  provenance: FinalStatsProvenance;
  contractVersion: string;
  assumptions: string[];
  warnings: string[];
  confidence: "high" | "medium" | "low";
}

export type FinalStatsResult =
  | { ok: true; stats: FinalCharacterStats }
  | { ok: false; kind: "empty" | "not_found" | "unsupported" | "engine_error"; message: string };

const FINAL_STATS_ASSUMPTIONS = Object.freeze([
  "Stats hors écran du jeu = valeurs de base + arme + artéfacts + ascension, SANS buffs conditionnels (résonance, passifs situationnels, food, sets 4p à condition).",
  "Une stat marquée « complète » correspond à l'écran du personnage ; « partielle » liste explicitement ce qui manque.",
  "Aucune stat n'est estimée : une donnée absente reste absente (jamais un 0 silencieux).",
]);

interface RawCell {
  value?: unknown;
  complete?: unknown;
  missing?: unknown;
}
interface RawCharacter {
  key?: string;
  level?: number;
  ascension?: number;
  constellation?: number;
  unsupported?: unknown;
  final_stats?: {
    complete?: boolean;
    note?: string;
    hp?: RawCell;
    atk?: RawCell;
    def?: RawCell;
    crit_rate_?: RawCell;
    crit_dmg_?: RawCell;
    eleMas?: RawCell;
    enerRech_?: RawCell;
    dmg_bonus?: Record<string, number>;
    weapon?: Record<string, unknown>;
  };
  provenance?: { snapshot_date?: string; source?: string; sha256?: string; good_version?: number };
}
interface RawPayload {
  status?: string;
  character?: RawCharacter;
}

function cell(raw: RawCell | undefined): FinalStatCell {
  const value =
    typeof raw?.value === "number" && Number.isFinite(raw.value) ? raw.value : null;
  const missing = Array.isArray(raw?.missing) ? raw!.missing.map(String) : [];
  return { value, complete: raw?.complete === true && value !== null, missing };
}

export function normalizeFinalStats(payload: RawPayload): FinalStatsResult {
  const status = payload?.status;
  if (status === "empty") {
    return { ok: false, kind: "empty", message: "Aucun personnage importé dans le scan du compte." };
  }
  const ch = payload?.character;
  if (!ch || !ch.key) {
    return { ok: false, kind: "not_found", message: "Personnage introuvable dans le scan." };
  }
  const fs = ch.final_stats;
  if (!fs) {
    // Perso présent mais base non supportée par le moteur (charstats l'indique via `unsupported`).
    return {
      ok: false,
      kind: "unsupported",
      message: "Stats de base du personnage non prises en charge par le moteur (jamais estimées).",
    };
  }

  const hp = cell(fs.hp);
  const atk = cell(fs.atk);
  const def = cell(fs.def);
  const critRate = cell(fs.crit_rate_);
  const critDamage = cell(fs.crit_dmg_);
  const elementalMastery = cell(fs.eleMas);
  const energyRecharge = cell(fs.enerRech_);

  // Avertissements = union honnête des « missing » de chaque cellule (dédupliqués).
  const warnings = [
    ...new Set(
      [hp, atk, def, critRate, critDamage, elementalMastery, energyRecharge].flatMap(
        (c) => c.missing,
      ),
    ),
  ];
  const complete = fs.complete === true;
  // Confiance dérivée de la complétude réelle : jamais « haute » si une donnée manque.
  const confidence: "high" | "medium" | "low" = complete
    ? "high"
    : warnings.length > 0
      ? "medium"
      : "low";

  const w = (fs.weapon ?? {}) as Record<string, unknown>;
  const numOrNull = (x: unknown): number | null =>
    typeof x === "number" && Number.isFinite(x) ? x : null;

  return {
    ok: true,
    stats: {
      key: ch.key,
      level: ch.level,
      ascension: ch.ascension,
      constellation: ch.constellation,
      complete,
      note: typeof fs.note === "string" ? fs.note : "",
      hp,
      atk,
      def,
      critRate,
      critDamage,
      elementalMastery,
      energyRecharge,
      damageBonuses: fs.dmg_bonus && typeof fs.dmg_bonus === "object" ? fs.dmg_bonus : {},
      weapon: {
        supported: w["supported"] === true,
        valid: w["valid"] === true,
        key: typeof w["key"] === "string" ? (w["key"] as string) : undefined,
        baseAtk: numOrNull(w["base_atk"]),
        secondaryStatKey:
          typeof w["secondary_stat_key"] === "string" ? (w["secondary_stat_key"] as string) : null,
        secondaryStatValue: numOrNull(w["secondary_stat_value"]),
      },
      provenance: {
        snapshotDate: ch.provenance?.snapshot_date,
        source: ch.provenance?.source,
        sha256: ch.provenance?.sha256,
        goodVersion: ch.provenance?.good_version,
      },
      contractVersion: FINAL_STATS_CONTRACT_VERSION,
      assumptions: [...FINAL_STATS_ASSUMPTIONS],
      warnings,
      confidence,
    },
  };
}
