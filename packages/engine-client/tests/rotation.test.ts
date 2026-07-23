import { describe, expect, it } from "vitest";
import { validateRotation, normalizeRotation, ROTATION_CONTRACT_VERSION } from "../src/rotation";
import type { RotationAction } from "../src/rotation";

const na = (over: Partial<RotationAction> = {}): RotationAction => ({
  id: "a1", actorId: "Bennett", kind: "normal_attack", startTime: 0, duration: 1,
  talentSlot: "combat1", talentLabel: "1-Hit DMG", talentLevel: 10, ...over,
});

describe("validateRotation (timeline pure, défense en profondeur)", () => {
  it("rotation vide / équipe vide → problèmes", () => {
    expect(validateRotation([], [])).toContain("Équipe vide.");
    expect(validateRotation(["Bennett"], [])).toContain(
      "Rotation vide : au moins une action requise.",
    );
  });

  it("timestamps/durées négatifs et NaN/Infinity rejetés", () => {
    expect(validateRotation(["Bennett"], [na({ startTime: -1 })]).some((s) => /début invalide/.test(s))).toBe(true);
    expect(validateRotation(["Bennett"], [na({ duration: Infinity })]).some((s) => /durée invalide/.test(s))).toBe(true);
  });

  it("acteur hors équipe + chevauchement détectés", () => {
    expect(validateRotation(["Bennett"], [na({ actorId: "Ganyu" })]).some((s) => /acteur absent/.test(s))).toBe(true);
    const overlap = [na({ startTime: 0, duration: 2 }), na({ id: "a2", startTime: 1, duration: 1 })];
    expect(validateRotation(["Bennett"], overlap).some((s) => /chevauchement/.test(s))).toBe(true);
  });

  it("rotation valide → aucun problème", () => {
    const acts = [na({ startTime: 0, duration: 1 }), na({ id: "a2", startTime: 1, duration: 1 })];
    expect(validateRotation(["Bennett"], acts)).toEqual([]);
  });
});

describe("normalizeRotation (adapter, jamais de faux DPS)", () => {
  it("mappe la sortie complète en camelCase", () => {
    const raw = {
      contract_version: ROTATION_CONTRACT_VERSION, duration: 2, actions: [],
      total_damage: 1000, average_damage_per_second: 500,
      damage_by_character: { Bennett: 1000 }, complete: true,
      assumptions: ["x"], warnings: [], provenance: { engine: "python" }, confidence: "high" as const,
    };
    const r = normalizeRotation(raw);
    expect(r.totalDamage).toBe(1000);
    expect(r.averageDamagePerSecond).toBe(500);
    expect(r.complete).toBe(true);
    expect(r.confidence).toBe("high");
  });

  it("rotation incomplète → DPS et total null (jamais fabriqués)", () => {
    const r = normalizeRotation({ complete: false, average_damage_per_second: null, total_damage: null, note: "rotation incomplète" });
    expect(r.averageDamagePerSecond).toBeNull();
    expect(r.totalDamage).toBeNull();
    expect(r.complete).toBe(false);
    expect(r.note).toMatch(/incomplète/);
  });
});
