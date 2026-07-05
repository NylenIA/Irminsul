import { describe, expect, it } from "vitest";
import { compareTeamPerformance, TEAM_COMPARE_CONTRACT_VERSION } from "../src/team-compare";
import type { RotationResult } from "../src/rotation";

const target = { level: 100, resistance: 0.1, count: 1 };

function rot(over: Partial<RotationResult> = {}): RotationResult {
  return {
    contractVersion: "rotation/1.0", duration: 10, actions: [],
    totalDamage: 100000, averageDamagePerSecond: 10000,
    damageByCharacter: {}, complete: true, assumptions: [], warnings: [],
    provenance: {}, confidence: "high", ...over,
  };
}

describe("compareTeamPerformance (team-compare/1.0 — jamais de verdict sur données incomplètes)", () => {
  it("deux rotations complètes → verdict quantitatif avec écart relatif", () => {
    const left = rot({ averageDamagePerSecond: 12000, totalDamage: 120000 });
    const right = rot({ averageDamagePerSecond: 10000, totalDamage: 100000 });
    const c = compareTeamPerformance("A", left, "B", right, target);
    expect(c.contractVersion).toBe(TEAM_COMPARE_CONTRACT_VERSION);
    expect(c.complete).toBe(true);
    expect(c.confidence).toBe("high");
    expect(c.verdict).toMatch(/A a un DPS supérieur de 16\.7 %/);
    const dps = c.differences.find((d) => d.metric === "DPS moyen")!;
    expect(dps.winner).toBe("left");
    expect(dps.absolute).toBe(2000);
  });

  it("une rotation incomplète → AUCUN verdict quantitatif (données insuffisantes)", () => {
    const left = rot({ complete: true });
    const right = rot({ complete: false, averageDamagePerSecond: null, totalDamage: null });
    const c = compareTeamPerformance("A", left, "B", right, target);
    expect(c.complete).toBe(false);
    expect(c.confidence).toBe("low");
    expect(c.verdict).toMatch(/Aucun verdict quantitatif fiable/);
    // La différence de DPS n'est pas calculable (right null).
    expect(c.differences.find((d) => d.metric === "DPS moyen")!.computable).toBe(false);
  });

  it("DPS égal → verdict d'équivalence (pas de faux gagnant)", () => {
    const c = compareTeamPerformance("A", rot(), "B", rot(), target);
    expect(c.verdict).toMatch(/équivalent/);
    expect(c.differences[0]!.winner).toBe("tie");
  });

  it("durée : plus court = mieux (higherIsBetter=false)", () => {
    const left = rot({ duration: 8 });
    const right = rot({ duration: 12 });
    const c = compareTeamPerformance("A", left, "B", right, target);
    const dur = c.differences.find((d) => d.metric === "Durée (s)")!;
    expect(dur.winner).toBe("left"); // 8s < 12s
  });

  it("hypothèses : même cible explicite, jamais un classement méta global", () => {
    const c = compareTeamPerformance("A", rot(), "B", rot(), target);
    expect(c.assumptions.join(" ")).toMatch(/MÊME cible/);
    expect(c.assumptions.join(" ")).toMatch(/pas un classement méta global/);
    expect(c.target).toEqual(target);
  });
});
