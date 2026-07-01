import { describe, expect, it } from "vitest";
import goldens from "./direct-hit.goldens.json";
import { calculateDirectHit, LocalEngineClient } from "../src/direct-hit";
import type { DirectHitInput } from "../src/contract";

/** snake_case Python -> camelCase TS. */
function toInput(raw: Record<string, number>): DirectHitInput {
  const map: Record<string, keyof DirectHitInput> = {
    scaling: "scaling",
    scaling_stat: "scalingStat",
    flat_base_damage: "flatBaseDamage",
    damage_bonus: "damageBonus",
    crit_rate: "critRate",
    crit_damage: "critDamage",
    attacker_level: "attackerLevel",
    enemy_level: "enemyLevel",
    enemy_resistance: "enemyResistance",
    defense_reduction: "defenseReduction",
    defense_ignore: "defenseIgnore",
    amplifying_reaction_multiplier: "amplifyingReactionMultiplier",
    reaction_bonus: "reactionBonus",
    vulnerability_multiplier: "vulnerabilityMultiplier",
  };
  const input: Record<string, number> = {};
  for (const [key, value] of Object.entries(raw)) {
    const mapped = map[key];
    if (!mapped) throw new Error(`Champ golden inconnu: ${key}`);
    input[mapped] = value;
  }
  return input as unknown as DirectHitInput;
}

describe("parité TS ↔ moteur Python (goldens générés par scripts/gen-engine-goldens.py)", () => {
  it.each(goldens.cases.map((c, i) => [i, c] as const))(
    "cas golden %d : résultats identiques à 1e-9 près",
    (_i, c) => {
      const result = calculateDirectHit(toInput(c.inputs as Record<string, number>));
      const expected = c.expected as Record<string, number>;
      expect(result.rawBase).toBeCloseTo(expected["raw_base"]!, 9);
      expect(result.nonCrit).toBeCloseTo(expected["non_crit"]!, 9);
      expect(result.crit).toBeCloseTo(expected["crit"]!, 9);
      expect(result.expected).toBeCloseTo(expected["expected"]!, 9);
      expect(result.defenseMultiplier).toBeCloseTo(expected["defense_multiplier"]!, 9);
      expect(result.resistanceMultiplier).toBeCloseTo(expected["resistance_multiplier"]!, 9);
      expect(result.expectedCritMultiplier).toBeCloseTo(expected["expected_crit_multiplier"]!, 9);
    },
  );

  it("rejette les entrées invalides comme le moteur Python", () => {
    expect(() => calculateDirectHit({ scaling: -1, scalingStat: 100 })).toThrow(RangeError);
    expect(() =>
      calculateDirectHit({ scaling: 1, scalingStat: 100, amplifyingReactionMultiplier: 0 }),
    ).toThrow(RangeError);
  });

  it("LocalEngineClient expose provenance + hypothèses (aucun faux DPS)", () => {
    const outcome = new LocalEngineClient().calculateDirectHit({ scaling: 1, scalingStat: 1000 });
    expect(outcome.provenance.engine).toBe("ts-port");
    expect(outcome.provenance.registryStatus).toBe("verified");
    expect(outcome.provenance.assumptions.length).toBeGreaterThan(0);
    expect(outcome.provenance.assumptions[0]).toMatch(/Coup isolé/);
  });
});
