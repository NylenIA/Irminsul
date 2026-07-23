/**
 * Portage TypeScript FIDÈLE de src/irminsul/reaction.py (formules KQM, registre sourcé).
 * Parité prouvée par goldens générés du moteur Python réel (tests/reaction.goldens.json).
 * v1 : réactions AMPLIFIANTES + TRANSFORMATIVES. Les additives (Aggravation/Propagation)
 * vivent sur la branche phase3 du moteur — hors périmètre tant qu'elle n'est pas fusionnée.
 * Les transformatives ne critiquent pas par défaut. Rien ici n'est un DPS de rotation.
 */
import { resistanceMultiplier } from "./direct-hit";

export const REACTION_CONTRACT_VERSION = "reactions/1.0";

/** Coefficient de niveau des transformatives — référence KQM, personnage niveau 90. */
export const LEVEL_MULTIPLIER_LV90 = 1446.85;

// Patch 5.2 : EC/Overload/Superconduct/Shatter buffés (voir docs/engine/FORMULA_SOURCES.md).
export const TRANSFORMATIVE_BASE = Object.freeze({
  swirl: 0.6,
  superconduct: 1.5,
  "electro-charged": 2.0,
  overloaded: 2.75,
  shattered: 3.0,
  burning: 0.25,
  bloom: 2.0,
  hyperbloom: 3.0,
  burgeon: 3.0,
} as const);

export const AMPLIFYING_BASE = Object.freeze({
  "forward-vaporize": 2.0,
  "reverse-vaporize": 1.5,
  "forward-melt": 2.0,
  "reverse-melt": 1.5,
} as const);

/**
 * Coefficients des réactions ADDITIVES (KQM ; porté de phase3 d61803b).
 * Le bonus s'AJOUTE à la base du coup (flatBaseDamage), puis DMG%/crit/DEF/RES.
 */
export const ADDITIVE_BASE = Object.freeze({
  aggravate: 1.15,
  spread: 1.25,
} as const);

export type TransformativeKind = keyof typeof TRANSFORMATIVE_BASE;
export type AmplifyingKind = keyof typeof AMPLIFYING_BASE;
export type AdditiveKind = keyof typeof ADDITIVE_BASE;

/** Alias acceptés par le moteur Python (parité : audit Codex B/C). */
const TRANSFORMATIVE_LOOKUP: Record<string, number> = Object.freeze({
  ...TRANSFORMATIVE_BASE,
  overload: 2.75,
  shatter: 3.0,
});

export function isTransformativeKind(key: string): boolean {
  return key in TRANSFORMATIVE_LOOKUP;
}
export function isAmplifyingKind(key: string): boolean {
  return key in AMPLIFYING_BASE;
}
export function isLunarKind(key: string): boolean {
  return key in LUNAR_BASE;
}
export function isAdditiveKind(key: string): boolean {
  return key in ADDITIVE_BASE;
}

function roundTo(value: number, digits: number): number {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

export function transformativeEmBonus(elementalMastery: number): number {
  const em = Math.max(elementalMastery, 0);
  return (16 * em) / (em + 2000);
}

export function amplifyingEmBonus(elementalMastery: number): number {
  const em = Math.max(elementalMastery, 0);
  return (2.78 * em) / (em + 1400);
}

export interface TransformativeResult {
  reaction: string;
  base_multiplier: number;
  level_multiplier: number;
  em_bonus: number;
  total_reaction_bonus: number;
  resistance_multiplier: number;
  damage: number;
}

export interface AmplifyingResult {
  reaction: string;
  base_multiplier: number;
  em_bonus: number;
  extra_bonus: number;
  amplifying_multiplier: number;
}

export function transformativeReaction(input: {
  reaction: string;
  elementalMastery?: number;
  levelMultiplier?: number;
  reactionBonus?: number;
  enemyResistance?: number;
}): TransformativeResult {
  const key = input.reaction.trim().toLowerCase();
  const base = TRANSFORMATIVE_LOOKUP[key];
  if (base === undefined) {
    throw new RangeError(
      `Réaction transformative inconnue : ${input.reaction}. Options : ${Object.keys(TRANSFORMATIVE_BASE).sort().join(", ")}`,
    );
  }
  const levelMultiplier = input.levelMultiplier ?? LEVEL_MULTIPLIER_LV90;
  if (levelMultiplier <= 0) throw new RangeError("levelMultiplier doit être positif");
  const emBonus = transformativeEmBonus(input.elementalMastery ?? 0);
  const totalBonus = emBonus + Math.max(input.reactionBonus ?? 0, 0);
  const resMult = resistanceMultiplier(input.enemyResistance ?? 0.1);
  const damage = base * levelMultiplier * (1 + totalBonus) * resMult;
  return {
    reaction: key,
    base_multiplier: base,
    level_multiplier: levelMultiplier,
    em_bonus: roundTo(emBonus, 4),
    total_reaction_bonus: roundTo(totalBonus, 4),
    resistance_multiplier: roundTo(resMult, 4),
    damage: roundTo(damage, 2),
  };
}

export function amplifyingMultiplier(input: {
  reaction: string;
  elementalMastery?: number;
  reactionBonus?: number;
}): AmplifyingResult {
  const key = input.reaction.trim().toLowerCase();
  const base = AMPLIFYING_BASE[key as AmplifyingKind];
  if (base === undefined) {
    throw new RangeError(
      `Réaction amplifiante inconnue : ${input.reaction}. Options : ${Object.keys(AMPLIFYING_BASE).sort().join(", ")}`,
    );
  }
  const emBonus = amplifyingEmBonus(input.elementalMastery ?? 0);
  const extra = Math.max(input.reactionBonus ?? 0, 0);
  const multiplier = base * (1 + emBonus + extra);
  return {
    reaction: key,
    base_multiplier: base,
    em_bonus: roundTo(emBonus, 4),
    extra_bonus: roundTo(extra, 4),
    amplifying_multiplier: roundTo(multiplier, 4),
  };
}

// --- Réactions lunaires (Luna I) — portage fidèle de lunar_reaction (Python) ---

/**
 * KQM distingue DEUX familles de dégâts lunaires (keqingmains.com/misc/lunar-reactions) :
 *  (1) dégâts de RÉACTION déclenchés : Lunar-Charged 1.8 (Electro) ·
 *      Lunar-Crystallize 1.6 (Géo, sans ICD global) — les multiplicateurs de LUNAR_BASE ;
 *  (2) dégâts lunaires DIRECTS de capacité (base plus élevée, pas de scaling niveau,
 *      pas de DMG% ordinaire, bonus EM lunaire + Lunar Reaction Base DMG Bonus).
 * Lunar-Bloom n'appartient QU'À (2) : KQM confirme qu'il « ne fait pas de dégâts
 * par lui-même » (cœurs -> Verdant Dew consommé par les capacités) → AUCUN
 * multiplicateur de réaction (pas « en attente » : inexistant par conception).
 */
export const LUNAR_BASE = Object.freeze({
  "lunar-charged": 1.8,
  "lunar-crystallize": 1.6,
} as const);

export type LunarKind = keyof typeof LUNAR_BASE;

/** Réactions lunaires reconnues mais sans dégâts de réaction propres (famille directe). */
export const LUNAR_ABILITY_ONLY: ReadonlySet<string> = new Set(["lunar-bloom"]);

/** Pondérations par dégâts personnels décroissants : 100 % / 50 % / 1/12 / 1/12. */
export const LUNAR_CONTRIBUTION_WEIGHTS = Object.freeze([1.0, 0.5, 1 / 12, 1 / 12] as const);

/** Bonus de Maîtrise lunaire : 6·EM/(EM+2000) (points publiés 500/1000/1500 EM). */
export function lunarEmBonus(elementalMastery: number): number {
  const em = Math.max(elementalMastery, 0);
  return (6 * em) / (em + 2000);
}

/** Bonus de Maîtrise additif : 5·EM/(EM+1200) (KQM). */
export function additiveEmBonus(elementalMastery: number): number {
  const em = Math.max(elementalMastery, 0);
  return (5 * em) / (em + 1200);
}

export interface AdditiveResult {
  reaction: string;
  base_multiplier: number;
  level_multiplier: number;
  em_bonus: number;
  extra_bonus: number;
  base_bonus_damage: number;
}

/**
 * Bonus de base additif Aggravation/Propagation — miroir exact de
 * `additive_reaction` (Python). À injecter via `flatBaseDamage` du coup direct.
 */
export function additiveReaction(input: {
  reaction: string;
  elementalMastery?: number;
  levelMultiplier?: number;
  reactionBonus?: number;
}): AdditiveResult {
  const key = input.reaction.trim().toLowerCase();
  const base = ADDITIVE_BASE[key as AdditiveKind];
  if (base === undefined) {
    throw new RangeError(
      `Réaction additive inconnue : ${input.reaction}. Options : ${Object.keys(ADDITIVE_BASE).sort().join(", ")}`,
    );
  }
  const levelMultiplier = input.levelMultiplier ?? LEVEL_MULTIPLIER_LV90;
  if (levelMultiplier <= 0) throw new RangeError("levelMultiplier doit être positif");
  const emBonus = additiveEmBonus(input.elementalMastery ?? 0);
  const extra = Math.max(input.reactionBonus ?? 0, 0);
  const bonus = base * levelMultiplier * (1 + emBonus + extra);
  return {
    reaction: key,
    base_multiplier: base,
    level_multiplier: levelMultiplier,
    em_bonus: roundTo(emBonus, 4),
    extra_bonus: roundTo(extra, 4),
    base_bonus_damage: roundTo(bonus, 2),
  };
}

export interface LunarContributorInput {
  elementalMastery?: number;
  critRate?: number;
  critDamage?: number;
  baseDmgBonus?: number;
  reactionBonus?: number;
}

export interface LunarContributorBreakdown {
  em_bonus: number;
  expected_crit_multiplier: number;
  base_dmg_bonus: number;
  reaction_bonus: number;
  personal_damage: number;
  weight: number;
  weighted_damage: number;
}

export interface LunarChargedResult {
  reaction: string;
  base_multiplier: number;
  level_multiplier: number;
  resistance_multiplier: number;
  contributors: LunarContributorBreakdown[];
  damage: number;
}

/**
 * Dégâts MOYENS d'une réaction lunaire multi-participants (ignore la DEF) —
 * miroir exact de `lunar_reaction` (Python). Espérance de crit par
 * contributeur ; agrégation triée par dégâts personnels décroissants.
 */
export function lunarReaction(input: {
  reaction: string;
  contributors: LunarContributorInput[];
  levelMultiplier?: number;
  enemyResistance?: number;
}): LunarChargedResult {
  const key = input.reaction.trim().toLowerCase();
  const baseFromKey = LUNAR_BASE[key as LunarKind];
  if (baseFromKey === undefined) {
    if (LUNAR_ABILITY_ONLY.has(key)) {
      throw new RangeError(
        "Lunar-Bloom ne produit pas de dégâts de réaction propres (KQM : la réaction " +
          "« does not deal damage on its own » — ses cœurs accumulent du Verdant Dew " +
          "consommé par les capacités). Ses dégâts sont des dégâts lunaires DIRECTS de " +
          "capacité : calcule-les via le coup direct (base = scaling de la capacité), avec " +
          "le bonus EM lunaire (lunarEmBonus) et le Lunar Reaction Base DMG Bonus, SANS " +
          "multiplicateur de niveau ni DMG% élémentaire ordinaire.",
      );
    }
    throw new RangeError(
      `Réaction lunaire inconnue : ${input.reaction}. Options : ${Object.keys(LUNAR_BASE).sort().join(", ")}`,
    );
  }
  const { contributors } = input;
  if (!contributors || contributors.length === 0) {
    throw new RangeError("contributors ne peut pas être vide (1 à 4 participants)");
  }
  if (contributors.length > LUNAR_CONTRIBUTION_WEIGHTS.length) {
    throw new RangeError(
      `Au plus ${LUNAR_CONTRIBUTION_WEIGHTS.length} contributeurs (équipe Genshin) ; reçu ${contributors.length}`,
    );
  }
  const levelMultiplier = input.levelMultiplier ?? LEVEL_MULTIPLIER_LV90;
  if (levelMultiplier <= 0) throw new RangeError("levelMultiplier doit être positif");

  const base = baseFromKey;
  const computed = contributors.map((raw) => {
    const emBonus = lunarEmBonus(raw.elementalMastery ?? 0);
    const critRate = Math.min(Math.max(raw.critRate ?? 0, 0), 1);
    const critDamage = Math.max(raw.critDamage ?? 0, 0);
    const expectedCrit = 1 + critRate * critDamage;
    const baseDmgBonus = Math.max(raw.baseDmgBonus ?? 0, 0);
    const reactionBonus = Math.max(raw.reactionBonus ?? 0, 0);
    const personal =
      base * levelMultiplier * (1 + baseDmgBonus) * (1 + reactionBonus + emBonus) * expectedCrit;
    return { emBonus, expectedCrit, baseDmgBonus, reactionBonus, personal };
  });

  computed.sort((a, b) => b.personal - a.personal); // tri stable (ES2019+), comme list.sort Python
  const resMult = resistanceMultiplier(input.enemyResistance ?? 0.1);
  let total = 0;
  const breakdown: LunarContributorBreakdown[] = computed.map((entry, rank) => {
    const weight = LUNAR_CONTRIBUTION_WEIGHTS[rank] ?? 0;
    const weighted = entry.personal * weight;
    total += weighted;
    return {
      em_bonus: roundTo(entry.emBonus, 4),
      expected_crit_multiplier: roundTo(entry.expectedCrit, 4),
      base_dmg_bonus: roundTo(entry.baseDmgBonus, 4),
      reaction_bonus: roundTo(entry.reactionBonus, 4),
      personal_damage: roundTo(entry.personal, 2),
      weight: roundTo(weight, 6),
      weighted_damage: roundTo(weighted * resMult, 2),
    };
  });

  return {
    reaction: key,
    base_multiplier: base,
    level_multiplier: levelMultiplier,
    resistance_multiplier: roundTo(resMult, 4),
    contributors: breakdown,
    damage: roundTo(total * resMult, 2),
  };
}

/** Compat : Lunar-Charged via `lunarReaction` (appelants existants). */
export function lunarChargedReaction(input: {
  contributors: LunarContributorInput[];
  levelMultiplier?: number;
  enemyResistance?: number;
}): LunarChargedResult {
  return lunarReaction({ reaction: "lunar-charged", ...input });
}

export const REACTION_PROVENANCE = Object.freeze({
  source: "src/irminsul/reaction.py (formules KQM)",
  version: REACTION_CONTRACT_VERSION,
  registryStatus: "verified" as const,
  assumptions: Object.freeze([
    "Une réaction isolée — pas une rotation ni un uptime d'aura.",
    "Transformatives : pas de critique (comportement de base) ; niveau 90 par défaut (1446.85).",
    "Amplifiantes : multiplicateur à injecter dans un coup direct (direction du déclenchement explicite).",
    "Additives (Aggravation 1.15 / Propagation 1.25) : bonus AJOUTÉ à la base du coup (flatBaseDamage), affecté ensuite par DMG%/crit/DEF/RES ; l'EM ne snapshot pas.",
    "Lunaires (Lunar-Charged 1.8 Électro ; Lunar-Crystallize 1.6 Géo) : valeur MOYENNE multi-contributeurs (espérance de crit par participant) ; ICD hors périmètre (rotation) ; Lunar-Bloom exclu (multiplicateur non confirmé — aucune valeur inventée).",
  ] as const),
});
