import { describe, expect, it } from "vitest";
import { normalizePlayerBuild, parseArtifactSets, parseWeaponRef } from "../src/player-build";

const PROFILE = { snapshot_date: "2026-06-26", source: "Inventory_Kamera", format: "GOOD" };

describe("normalizePlayerBuild (adapter scan GOOD — aucune stat inventée)", () => {
  it("normalise un personnage scanné complet avec provenance et confiance", () => {
    const build = normalizePlayerBuild(
      {
        key: "Mavuika",
        level: 90,
        ascension: 6,
        constellation: 0,
        talents: { auto: 1, skill: 8, burst: 9 },
        weapon: "w-008-WolfsGravestone-r1-055aea9d",
        artifacts: { flower: "a", plume: "b", sands: "c", circlet: "d", goblet: "e" },
      },
      PROFILE,
    );
    expect(build).not.toBeNull();
    expect(build?.level).toBe(90);
    expect(build?.talents).toEqual({ normal: 1, skill: 8, burst: 9 });
    expect(build?.weapon).toEqual({ id: "WolfsGravestone", refinement: 1 });
    expect(build?.artifactSlots).toHaveLength(5);
    expect(build?.source).toBe("scanner");
    expect(build?.importedAt).toBe("2026-06-26");
    expect(build?.confidence).toBe("high");
    // Les stats finales ne sont JAMAIS estimées sur cette branche.
    expect(build?.missing.join(" ")).toMatch(/stats finales/);
  });

  it("liste les champs absents au lieu de les inventer", () => {
    const build = normalizePlayerBuild({ key: "Zibai" }, PROFILE);
    expect(build?.missing).toEqual(
      expect.arrayContaining(["niveau", "talents", "arme"]),
    );
  });

  it("parseArtifactSets : compte les pièces par set depuis les réfs réelles", () => {
    const sets = parseArtifactSets({
      flower: "a-038-ObsidianCodex-flower-0ca98fd8",
      plume: "a-039-ObsidianCodex-plume-79523af3",
      sands: "a-040-ObsidianCodex-sands-bbf1fe9a",
      circlet: "a-041-ObsidianCodex-circlet-e47d7247",
      goblet: "a-147-GladiatorsFinale-goblet-dbbad8f8",
    });
    expect(sets).toEqual([
      { set: "ObsidianCodex", count: 4 },
      { set: "GladiatorsFinale", count: 1 },
    ]);
    expect(parseArtifactSets(undefined)).toEqual([]);
    expect(parseArtifactSets({ flower: "ref-invalide" })).toEqual([]);
  });

  it("retourne null si le personnage n'est pas scanné ; parseWeaponRef robuste", () => {
    expect(normalizePlayerBuild(undefined, PROFILE)).toBeNull();
    expect(parseWeaponRef(undefined)).toBeUndefined();
    expect(parseWeaponRef("format-inattendu")).toEqual({ id: "format-inattendu" });
  });
});
