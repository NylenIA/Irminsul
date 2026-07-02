import { describe, expect, it } from "vitest";
import { buildDirectHitPreview } from "../src/preview";
import { calculateDirectHit } from "../src/direct-hit";
import { ENGINE_CONTRACT_VERSION } from "../src/contract";

const VALID = { character: "Bennett", scalingPct: 250, scalingStat: 2000 };

describe("buildDirectHitPreview (orchestration pure, sans formule dupliquée)", () => {
  it("calcule un aperçu complet : conversion %→décimal identique au moteur", () => {
    const res = buildDirectHitPreview({
      ...VALID,
      critRatePct: 60,
      critDamagePct: 120,
      damageBonusPct: 46.6,
      enemyLevel: 103,
      enemyResistancePct: 10,
      attackerLevel: 90,
    });
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    const direct = calculateDirectHit({
      scaling: 2.5,
      scalingStat: 2000,
      critRate: 0.6,
      critDamage: 1.2,
      damageBonus: 0.466,
      enemyLevel: 103,
      enemyResistance: 0.1,
      attackerLevel: 90,
    });
    expect(res.preview.outcome.result).toEqual(direct);
    expect(res.preview.defaultsUsed).toEqual([]);
    expect(res.preview.contractVersion).toBe(ENGINE_CONTRACT_VERSION);
  });

  it("applique les défauts du moteur et les LISTE (transparence)", () => {
    const res = buildDirectHitPreview(VALID);
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    expect(res.preview.defaultsUsed).toEqual([
      "critRatePct",
      "critDamagePct",
      "damageBonusPct",
      "enemyLevel",
      "enemyResistancePct",
      "attackerLevel",
    ]);
    expect(res.preview.parameters["critRate"]).toBe(0.05);
    expect(res.preview.parameters["enemyResistance"]).toBe(0.1);
  });

  it("insufficient_data : champs requis manquants, rien d'inventé", () => {
    const res = buildDirectHitPreview({ character: "", scalingPct: null, scalingStat: 2000 });
    expect(res).toEqual({
      ok: false,
      kind: "insufficient_data",
      issues: ["character", "scalingPct"],
    });
  });

  it("validation_error : bornes et non-finis rejetés avant le moteur", () => {
    const bad = buildDirectHitPreview({
      ...VALID,
      scalingPct: Infinity,
    });
    expect(bad.ok).toBe(false);
    if (bad.ok) return;
    expect(bad.kind).toBe("validation_error");

    const outOfRange = buildDirectHitPreview({ ...VALID, critRatePct: 250 });
    expect(outOfRange.ok).toBe(false);
    if (outOfRange.ok) return;
    expect(outOfRange.kind).toBe("validation_error");
    expect(outOfRange.issues.join(" ")).toMatch(/critRatePct/);
  });

  it("provenance + hypothèses + confiance présentes (aucun faux DPS)", () => {
    const res = buildDirectHitPreview(VALID);
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    expect(res.preview.outcome.provenance.engine).toBe("ts-port");
    expect(res.preview.outcome.provenance.registryStatus).toBe("verified");
    expect(res.preview.outcome.provenance.assumptions[0]).toMatch(/Coup isolé/);
    expect(res.preview.confidence.level).toBe("haute");
  });
});
