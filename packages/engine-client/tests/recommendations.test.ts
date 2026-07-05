import { describe, expect, it } from "vitest";
import { buildRecommendations, RECOMMENDATIONS_CONTRACT_VERSION } from "../src/recommendations";
import type { PlayerCharacterBuild } from "../src/player-build";

function build(id: string, over: Partial<PlayerCharacterBuild> = {}): PlayerCharacterBuild {
  return {
    characterId: id, level: 90, constellation: 0,
    talents: { normal: 1, skill: 8, burst: 9 },
    weapon: { id: "Wep", refinement: 1 },
    artifactSlots: ["flower", "plume", "sands", "goblet", "circlet"],
    source: "scanner", confidence: "high", missing: [], ...over,
  };
}
const PROV = { source: "Inventory_Kamera", importedAt: "2026-06-26" };

describe("buildRecommendations (recommendations/1.0 — explicable, données réelles seulement)", () => {
  it("data_quality : signale les builds incomplets avec preuves réelles", () => {
    const builds = [build("Full"), build("NoWeapon", { weapon: undefined })];
    const r = buildRecommendations(
      { objective: "data_quality", availableCharacterIds: ["Full", "NoWeapon"] },
      builds, [], PROV,
    );
    expect(r.contractVersion).toBe(RECOMMENDATIONS_CONTRACT_VERSION);
    const noWep = r.recommendations.find((x) => x.title.includes("NoWeapon"));
    expect(noWep).toBeDefined();
    expect(noWep!.evidence.join(" ")).toMatch(/arme/);
    expect(noWep!.type).toBe("weapon");
    expect(noWep!.expectedImpact).toBe("améliore la fiabilité du calcul");
    // Provenance présente, jamais de chemin local.
    expect(r.provenance[0]!.source).toBe("Inventory_Kamera");
  });

  it("ne recommande JAMAIS un personnage non possédé ; respecte les exclusions", () => {
    const builds = [build("Owned"), build("Excluded")];
    const r = buildRecommendations(
      { objective: "data_quality", availableCharacterIds: ["Owned", "Excluded"], constraints: { excludedCharacterIds: ["Excluded"] } },
      builds, [], PROV,
    );
    expect(r.recommendations.some((x) => x.title.includes("Excluded"))).toBe(false);
  });

  it("improve_current_team : identifie le goulot d'étranglement (build le plus incomplet)", () => {
    const builds = [build("Good"), build("Weak", { weapon: undefined, talents: undefined })];
    const r = buildRecommendations(
      { objective: "improve_current_team", availableCharacterIds: ["Good", "Weak"], currentTeamId: "t1" },
      builds, [{ id: "t1", name: "Ma Team", members: ["Good", "Weak"] }], PROV,
    );
    const bottleneck = r.recommendations[0]!;
    expect(bottleneck.title).toMatch(/Goulot.*Weak/);
    expect(bottleneck.evidence.join(" ")).toMatch(/arme|talents/);
  });

  it("highest_complete_dps : classe les équipes par complétude réelle des membres", () => {
    const builds = [build("A"), build("B"), build("C", { artifactSlots: ["flower"] })];
    const teams = [
      { id: "full", name: "Full", members: ["A", "B"] },
      { id: "partial", name: "Partial", members: ["A", "C"] },
    ];
    const r = buildRecommendations(
      { objective: "highest_complete_dps", availableCharacterIds: ["A", "B", "C"] },
      builds, teams, PROV,
    );
    expect(r.recommendations[0]!.title).toMatch(/Full — 2\/2/);
    expect(r.recommendations[0]!.confidence).toBe("high");
    const partial = r.recommendations.find((x) => x.title.includes("Partial"))!;
    expect(partial.confidence).toBe("medium"); // 1/2 complet
  });

  it("objectif non modélisé → recommandation qualitative + missingData (jamais de faux chiffre)", () => {
    const r = buildRecommendations(
      { objective: "survivability", availableCharacterIds: ["A"] },
      [build("A")], [], PROV,
    );
    expect(r.recommendations[0]!.expectedImpact).toBe("non quantifié");
    expect(r.recommendations[0]!.confidence).toBe("low");
    expect(r.missingData.join(" ")).toMatch(/non encore modélisés/);
  });

  it("aucun personnage possédé → missingData explicite", () => {
    const r = buildRecommendations(
      { objective: "data_quality", availableCharacterIds: [] }, [], [], null,
    );
    expect(r.missingData.join(" ")).toMatch(/Aucun personnage possédé/);
    expect(r.confidence).toBe("high"); // "aucune donnée manquante" est une reco haute confiance sur 0 perso...
  });
});
