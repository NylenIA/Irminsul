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

export const TRANSFORMATIVE_BASE = Object.freeze({
  swirl: 0.6,
  superconduct: 0.5,
  "electro-charged": 1.2,
  overloaded: 2.0,
  shattered: 1.5,
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

export type TransformativeKind = keyof typeof TRANSFORMATIVE_BASE;
export type AmplifyingKind = keyof typeof AMPLIFYING_BASE;

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
  const base = TRANSFORMATIVE_BASE[key as TransformativeKind];
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

export const REACTION_PROVENANCE = Object.freeze({
  source: "src/irminsul/reaction.py (formules KQM)",
  version: REACTION_CONTRACT_VERSION,
  registryStatus: "verified" as const,
  assumptions: Object.freeze([
    "Une réaction isolée — pas une rotation ni un uptime d'aura.",
    "Transformatives : pas de critique (comportement de base) ; niveau 90 par défaut (1446.85).",
    "Amplifiantes : multiplicateur à injecter dans un coup direct (direction du déclenchement explicite).",
    "Additives (Aggravation/Propagation) : hors périmètre v1 (moteur phase3 non fusionné).",
  ] as const),
});
