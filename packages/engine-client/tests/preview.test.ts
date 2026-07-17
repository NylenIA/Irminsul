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

  it("réaction amplifiante : multiplicateur injecté dans le coup + détail exposé", () => {
    const withReaction = buildDirectHitPreview({ ...VALID, reaction: "forward-vaporize", elementalMastery: 187 });
    const without = buildDirectHitPreview(VALID);
    expect(withReaction.ok && without.ok).toBe(true);
    if (!withReaction.ok || !without.ok) return;
    expect(withReaction.preview.reaction?.type).toBe("amplifying");
    const mult = withReaction.preview.parameters["amplifyingReactionMultiplier"]!;
    expect(mult).toBeGreaterThan(2); // ×2 de base + bonus EM
    expect(withReaction.preview.outcome.result.expected).toBeCloseTo(
      without.preview.outcome.result.expected * mult, 6,
    );
  });

  it("réaction transformative : dégâts propres, coup direct inchangé ; réaction inconnue rejetée", () => {
    const res = buildDirectHitPreview({ ...VALID, reaction: "hyperbloom", elementalMastery: 1000 });
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    expect(res.preview.reaction?.type).toBe("transformative");
    expect(res.preview.parameters["amplifyingReactionMultiplier"]).toBeUndefined();
    if (res.preview.reaction?.type === "transformative") {
      expect(res.preview.reaction.detail.damage).toBeGreaterThan(0);
    }
    const bad = buildDirectHitPreview({ ...VALID, reaction: "freeze" });
    expect(bad.ok).toBe(false);
    if (!bad.ok) expect(bad.kind).toBe("validation_error");
  });

  it("réaction lunaire : dégâts moyens avec crit du contributeur, coup direct inchangé", () => {
    const res = buildDirectHitPreview({
      ...VALID,
      reaction: "lunar-charged",
      elementalMastery: 1000,
      critRatePct: 50,
      critDamagePct: 100,
      enemyResistancePct: 0,
    });
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    expect(res.preview.reaction?.type).toBe("lunar");
    expect(res.preview.parameters["amplifyingReactionMultiplier"]).toBeUndefined();
    if (res.preview.reaction?.type === "lunar") {
      const detail = res.preview.reaction.detail;
      // 1 contributeur : 1.8 × 1446.85 × (1+2.0) × (1 + 0.5×1.0) = 11719.485
      expect(detail.contributors).toHaveLength(1);
      expect(detail.contributors[0]!.expected_crit_multiplier).toBeCloseTo(1.5, 9);
      expect(detail.damage).toBeCloseTo(11719.49, 2);
    }
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
