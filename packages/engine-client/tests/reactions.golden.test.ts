import { describe, expect, it } from "vitest";
import goldens from "./reaction.goldens.json";
import {
  amplifyingMultiplier,
  lunarChargedReaction,
  lunarReaction,
  transformativeReaction,
  REACTION_PROVENANCE,
} from "../src/reactions";

type Num = Record<string, number | string>;

function camelInputs(raw: Record<string, unknown>) {
  return {
    reaction: raw["reaction"] as string,
    elementalMastery: raw["elemental_mastery"] as number | undefined,
    levelMultiplier: raw["level_multiplier"] as number | undefined,
    reactionBonus: raw["reaction_bonus"] as number | undefined,
    enemyResistance: raw["enemy_resistance"] as number | undefined,
  };
}

describe("parité réactions TS ↔ moteur Python (goldens gen-reaction-goldens.py)", () => {
  it.each(goldens.amplifying.map((c, i) => [i, c] as const))(
    "amplifiante golden %d",
    (_i, c) => {
      const result = amplifyingMultiplier(camelInputs(c.inputs)) as unknown as Num;
      for (const [key, expected] of Object.entries(c.expected as Num)) {
        if (typeof expected === "number") expect(result[key]).toBeCloseTo(expected, 9);
        else expect(result[key]).toBe(expected);
      }
    },
  );

  it.each(goldens.transformative.map((c, i) => [i, c] as const))(
    "transformative golden %d",
    (_i, c) => {
      const result = transformativeReaction(camelInputs(c.inputs)) as unknown as Num;
      for (const [key, expected] of Object.entries(c.expected as Num)) {
        if (typeof expected === "number") expect(result[key]).toBeCloseTo(expected, 9);
        else expect(result[key]).toBe(expected);
      }
    },
  );

  it.each(goldens.lunar.map((c, i) => [i, c] as const))("lunaire golden %d", (_i, c) => {
    const inputs = c.inputs as Record<string, unknown>;
    const result = lunarReaction({
      reaction: inputs["reaction"] as string,
      contributors: (inputs["contributors"] as Record<string, number | undefined>[]).map((raw) => ({
        elementalMastery: raw["elemental_mastery"],
        critRate: raw["crit_rate"],
        critDamage: raw["crit_damage"],
        baseDmgBonus: raw["base_dmg_bonus"],
        reactionBonus: raw["reaction_bonus"],
      })),
      levelMultiplier: inputs["level_multiplier"] as number | undefined,
      enemyResistance: inputs["enemy_resistance"] as number | undefined,
    });
    for (const [key, exp] of Object.entries(c.expected as Record<string, unknown>)) {
      if (key === "contributors") {
        const expList = exp as Record<string, number>[];
        expect(result.contributors).toHaveLength(expList.length);
        expList.forEach((expC, j) => {
          const got = result.contributors[j] as unknown as Record<string, number>;
          for (const [ck, cv] of Object.entries(expC)) expect(got[ck]).toBeCloseTo(cv, 9);
        });
      } else if (typeof exp === "number") {
        expect((result as unknown as Num)[key]).toBeCloseTo(exp, 9);
      } else {
        expect((result as unknown as Num)[key]).toBe(exp);
      }
    }
  });

  it("lunaire : validations (vide, >4 contributeurs, niveau invalide, réaction inconnue)", () => {
    expect(() => lunarReaction({ reaction: "lunar-bloom", contributors: [{}] })).toThrow(
      RangeError,
    );
    expect(() => lunarChargedReaction({ contributors: [] })).toThrow(RangeError);
    expect(() => lunarChargedReaction({ contributors: [{}, {}, {}, {}, {}] })).toThrow(RangeError);
    expect(() => lunarChargedReaction({ contributors: [{}], levelMultiplier: 0 })).toThrow(
      RangeError,
    );
  });

  it("rejette les réactions inconnues et level_multiplier invalide", () => {
    expect(() => transformativeReaction({ reaction: "freeze" })).toThrow(RangeError);
    expect(() => transformativeReaction({ reaction: "swirl", levelMultiplier: 0 })).toThrow(RangeError);
    expect(() => amplifyingMultiplier({ reaction: "aggravate" })).toThrow(RangeError);
  });

  it("provenance : source, version, hypothèses (additives explicitement hors périmètre)", () => {
    expect(REACTION_PROVENANCE.source).toMatch(/reaction\.py/);
    expect(REACTION_PROVENANCE.assumptions.join(" ")).toMatch(/Additives .* hors périmètre/);
  });
});
