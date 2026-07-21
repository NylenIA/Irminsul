import { describe, expect, it } from "vitest";
import {
  GCSIM_CONFIG_CONTRACT_VERSION,
  normalizeGcsimKey,
  teamToGcsimSkeleton,
} from "../src/gcsim-config";

describe("normalizeGcsimKey", () => {
  it("minuscule + alphanumérique, diacritiques et espaces retirés", () => {
    expect(normalizeGcsimKey("Bennett")).toBe("bennett");
    expect(normalizeGcsimKey("Hu Tao")).toBe("hutao");
    expect(normalizeGcsimKey("Raiden Shogun")).toBe("raidenshogun");
    expect(normalizeGcsimKey("Kūki")).toBe("kuki");
    expect(normalizeGcsimKey("Yae Miko")).toBe("yaemiko");
  });
});

describe("teamToGcsimSkeleton", () => {
  it("rejette une équipe vide et > 4 membres", () => {
    expect(() => teamToGcsimSkeleton([])).toThrow(RangeError);
    expect(() => teamToGcsimSkeleton([{ character: "", slot: 0 }])).toThrow(RangeError);
    expect(() =>
      teamToGcsimSkeleton([0, 1, 2, 3, 4].map((slot) => ({ character: `C${slot}`, slot }))),
    ).toThrow(RangeError);
  });

  it("trie par slot, génère un header + un bloc par personnage, active le premier", () => {
    const out = teamToGcsimSkeleton([
      { character: "Xingqiu", slot: 2 },
      { character: "Bennett", slot: 0 },
      { character: "Hu Tao", slot: 1 },
    ]);
    // Ordre par slot : Bennett (0) actif, puis Hu Tao, puis Xingqiu.
    expect(out).toMatch(/active bennett;/);
    const firstChar = out.indexOf("bennett char");
    const secondChar = out.indexOf("hutao char");
    const thirdChar = out.indexOf("xingqiu char");
    expect(firstChar).toBeGreaterThan(-1);
    expect(firstChar).toBeLessThan(secondChar);
    expect(secondChar).toBeLessThan(thirdChar);
    // Header options/target présent (config syntaxiquement plausible).
    expect(out).toMatch(/options iteration=\d+ duration=\d+/);
    expect(out).toMatch(/target lvl=100 resist=0\.1/);
  });

  it("honnêteté : TODO explicites sur arme/set/stats/rotation, jamais de valeur inventée", () => {
    const out = teamToGcsimSkeleton([{ character: "Bennett", slot: 0 }]);
    expect(out).toMatch(/PAS une simulation/);
    expect(out).toContain('weapon="TODO"');
    expect(out).toContain('set="TODO"');
    expect(out).toMatch(/TODO stats reelles/);
    expect(out).toMatch(/TODO rotation/);
    // Le nom source est annoté pour corriger une cle erronee.
    expect(out).toMatch(/depuis "Bennett" — verifier la cle gcsim/);
  });

  it("expose une version de contrat", () => {
    expect(GCSIM_CONFIG_CONTRACT_VERSION).toBe("gcsim-config/1.0");
  });
});
