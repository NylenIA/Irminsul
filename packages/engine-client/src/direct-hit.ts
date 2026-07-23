/**
 * Portage TypeScript FIDÈLE de src/irminsul/damage.py::calculate_direct_hit
 * (registre des mécaniques : `verified`). Même ordre d'opérations, mêmes clamps,
 * même branche piecewise de résistance. La parité est prouvée par les goldens
 * générés depuis le moteur Python réel (tests/direct-hit.goldens.json).
 */
import {
  DIRECT_HIT_ASSUMPTIONS,
  type DirectHitInput,
  type DirectHitOutcome,
  type DirectHitResult,
  type EngineClient,
} from "./contract";

export function resistanceMultiplier(resistance: number): number {
  if (resistance < 0) return 1 - resistance / 2;
  if (resistance < 0.75) return 1 - resistance;
  return 1 / (4 * resistance + 1);
}

export function defenseMultiplier(
  attackerLevel: number,
  enemyLevel: number,
  defenseReduction = 0,
  defenseIgnore = 0,
): number {
  const reduction = Math.min(Math.max(defenseReduction, 0), 0.99);
  const ignore = Math.min(Math.max(defenseIgnore, 0), 0.99);
  const numerator = attackerLevel + 100;
  const denominator = numerator + (enemyLevel + 100) * (1 - reduction) * (1 - ignore);
  return numerator / denominator;
}

export function calculateDirectHit(input: DirectHitInput): DirectHitResult {
  const {
    scaling,
    scalingStat,
    flatBaseDamage = 0,
    damageBonus = 0,
    attackerLevel = 90,
    enemyLevel = 100,
    enemyResistance = 0.1,
    defenseReduction = 0,
    defenseIgnore = 0,
    amplifyingReactionMultiplier = 1,
    reactionBonus = 0,
    vulnerabilityMultiplier = 1,
  } = input;

  if (scaling < 0 || scalingStat < 0) {
    throw new RangeError("scaling and scalingStat must be non-negative");
  }
  if (amplifyingReactionMultiplier <= 0 || vulnerabilityMultiplier <= 0) {
    throw new RangeError("multipliers must be positive");
  }

  const critRate = Math.min(Math.max(input.critRate ?? 0.05, 0), 1);
  const critDamage = Math.max(input.critDamage ?? 0.5, 0);
  const rawBase = scaling * scalingStat + flatBaseDamage;
  const defMult = defenseMultiplier(attackerLevel, enemyLevel, defenseReduction, defenseIgnore);
  const resMult = resistanceMultiplier(enemyResistance);
  const reaction = amplifyingReactionMultiplier * (1 + Math.max(reactionBonus, 0));
  const nonCrit =
    rawBase * (1 + damageBonus) * reaction * defMult * resMult * vulnerabilityMultiplier;
  const crit = nonCrit * (1 + critDamage);
  const expectedCritMultiplier = 1 + critRate * critDamage;
  const expected = nonCrit * expectedCritMultiplier;

  return {
    rawBase,
    nonCrit,
    crit,
    expected,
    defenseMultiplier: defMult,
    resistanceMultiplier: resMult,
    expectedCritMultiplier,
  };
}

/** Implémentation locale (TS) du contrat — provenance explicite, hypothèses visibles. */
export class LocalEngineClient implements EngineClient {
  calculateDirectHit(input: DirectHitInput): DirectHitOutcome {
    return {
      result: calculateDirectHit(input),
      provenance: {
        engine: "ts-port",
        formula: "direct_hit@irminsul-damage",
        registryStatus: "verified",
        assumptions: DIRECT_HIT_ASSUMPTIONS,
      },
    };
  }
}
