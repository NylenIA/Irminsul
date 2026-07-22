import { describe, expect, it } from "vitest";
import {
  GCSIM_CONFIG_CONTRACT_VERSION,
  ascensionMaxLevel,
  normalizeGcsimKey,
  teamToGcsimSkeleton,
} from "../src/gcsim-config";

describe("ascensionMaxLevel", () => {
  it("mappe chaque phase A0..A6 sur son cap ; défaut 90 hors bornes", () => {
    expect([0, 1, 2, 3, 4, 5, 6].map(ascensionMaxLevel)).toEqual([20, 40, 50, 60, 70, 80, 90]);
    expect(ascensionMaxLevel(undefined)).toBe(90);
    expect(ascensionMaxLevel(99)).toBe(90);
  });
});

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
    expect(out).toMatch(/TODO stats substats reelles/);
    expect(out).toMatch(/TODO rotation/);
    // Le nom source est annoté pour corriger une cle erronee.
    expect(out).toMatch(/depuis "Bennett" — verifier la cle gcsim/);
  });

  it("enrichit depuis un build réel (perso/arme/set) ; stats restent TODO", () => {
    const out = teamToGcsimSkeleton([{ character: "Hu Tao", slot: 0 }], {
      builds: {
        "Hu Tao": {
          level: 80,
          ascension: 6,
          constellation: 1,
          talents: { normal: 10, skill: 8, burst: 9 },
          weapon: { id: "StaffOfHoma", refinement: 1 },
          artifactSets: [{ set: "CrimsonWitchOfFlames", count: 4 }],
        },
      },
    });
    expect(out).toMatch(/hutao char lvl=80\/90 cons=1 talent=10,8,9;/);
    expect(out).toContain('hutao add weapon="staffofhoma" refine=1 lvl=90/90;');
    expect(out).toContain('hutao add set="crimsonwitchofflames" count=4;');
    // Sans stats substat fournies -> TODO honnête, jamais inventé.
    expect(out).toMatch(/TODO stats substats reelles/);
    expect(out).not.toContain('weapon="TODO"');
  });

  it("émet une ligne add stats réelle quand artifactStats fourni (sinon TODO)", () => {
    const out = teamToGcsimSkeleton([{ character: "Bennett", slot: 0 }], {
      builds: {
        Bennett: {
          weapon: { id: "AquilaFavonia", refinement: 1 },
          artifactStats: { hp: 4780, atk: 311, "atk%": 0.559, cr: 0.109, cd: 0.7, em: 40 },
        },
      },
    });
    expect(out).toMatch(/bennett add stats [^;]*atk%=0\.559[^;]*; \/\/ somme artefacts/);
    expect(out).toContain("hp=4780");
    expect(out).toContain("cd=0.7");
    expect(out).not.toMatch(/bennett add stats hp=0 atk=0 em=0/); // pas le TODO
  });

  it("sans build -> tout en TODO (comportement d'origine préservé)", () => {
    const out = teamToGcsimSkeleton([{ character: "Bennett", slot: 0 }]);
    expect(out).toContain('weapon="TODO"');
    expect(out).toContain('set="TODO"');
    expect(out).toMatch(/bennett char lvl=90\/90 cons=0 talent=9,9,9;/);
  });

  it("expose une version de contrat", () => {
    expect(GCSIM_CONFIG_CONTRACT_VERSION).toBe("gcsim-config/1.0");
  });
});
