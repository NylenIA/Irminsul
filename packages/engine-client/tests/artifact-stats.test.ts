import { describe, expect, it } from "vitest";
import { sumArtifactStats, type GoodArtifactLike } from "../src/artifact-stats";

const art = (
  mainStatKey: string,
  substats: [string, number][],
  over: Partial<GoodArtifactLike> = {},
): GoodArtifactLike => ({
  rarity: 5,
  level: 20,
  mainStatKey,
  substats: substats.map(([key, value]) => ({ key, value })),
  ...over,
});

describe("sumArtifactStats", () => {
  it("somme main (table 5★ niv20) + substats, en clés/décimales gcsim", () => {
    const res = sumArtifactStats([
      art("hp", [["critRate_", 3.9], ["atk_", 9.3]]), // fleur : HP plat main
      art("atk", [["critDMG_", 7.8], ["eleMas", 40]]), // plume : ATQ plat main
      art("atk_", [["critRate_", 3.1]]), // sablier : ATQ% main 0.466
      art("pyro_dmg_", [["atk_", 5.8]]), // coupe : Pyro% main 0.466
      art("critDMG_", [["critRate_", 3.9]]), // couronne : CD% main 0.622
    ]);
    expect(res.complete).toBe(true);
    // Mains plats + %.
    expect(res.stats["hp"]).toBe(4780);
    expect(res.stats["atk"]).toBe(311);
    expect(res.stats["atk%"]).toBeCloseTo(0.466 + 0.093 + 0.058, 4); // main + 2 subs
    expect(res.stats["pyro%"]).toBeCloseTo(0.466, 4);
    // Crit : substats (3.9+3.1+3.9=10.9% -> 0.109) + main CD 0.622 + sub CD 0.078.
    expect(res.stats["cr"]).toBeCloseTo(0.109, 4);
    expect(res.stats["cd"]).toBeCloseTo(0.622 + 0.078, 4);
    expect(res.stats["em"]).toBe(40);
  });

  it("gate : un artéfact non 5★-niv20 rend le total incomplet (jamais approximé)", () => {
    const four = art("atk_", [], { rarity: 4 });
    const notMax = art("hp_", [], { level: 16 });
    expect(sumArtifactStats([four]).complete).toBe(false);
    expect(sumArtifactStats([notMax]).complete).toBe(false);
    expect(sumArtifactStats([]).complete).toBe(false);
  });

  it("ignore les clés de stat inconnues sans planter", () => {
    const res = sumArtifactStats([art("atk_", [["mystery_stat", 99]])]);
    expect(res.stats["atk%"]).toBeCloseTo(0.466, 4);
    expect(Object.keys(res.stats)).not.toContain("mystery_stat");
  });
});
