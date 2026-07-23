import { describe, expect, it } from "vitest";
import { rotationToGcsimActions } from "../src/gcsim-rotation";

const a = (actorId: string, kind: string) => ({ actorId, kind });

describe("rotationToGcsimActions", () => {
  it("mappe les types vers les verbes gcsim et groupe par personnage actif", () => {
    const out = rotationToGcsimActions([
      a("Bennett", "skill"),
      a("Bennett", "burst"),
      a("Hu Tao", "skill"),
      a("Hu Tao", "charged_attack"),
      a("Hu Tao", "normal_attack"),
    ]);
    expect(out).toMatch(/active bennett;/);
    expect(out).toContain("bennett skill, burst;");
    expect(out).toContain("hutao skill, charge, attack;");
  });

  it("swap change l'acteur sans verbe ; plunge et cle normalisee", () => {
    const out = rotationToGcsimActions([
      a("Raiden Shogun", "burst"),
      a("Xingqiu", "swap"),
      a("Xingqiu", "plunging_attack"),
    ]);
    expect(out).toContain("raidenshogun burst;");
    expect(out).toContain("xingqiu high_plunge;");
  });

  it("honnêteté : bandeau non-modélisé ; mention des waits si présents", () => {
    const out = rotationToGcsimActions([a("Bennett", "skill"), a("Bennett", "wait")]);
    expect(out).toMatch(/ORDRE des actions seulement/);
    expect(out).toMatch(/temps d'attente NON modelises/);
    // le wait n'ajoute pas de verbe
    expect(out).toContain("bennett skill;");
  });

  it("rejette une rotation sans action exportable (que des waits/swaps)", () => {
    expect(() => rotationToGcsimActions([a("Bennett", "wait"), a("Bennett", "swap")])).toThrow(
      RangeError,
    );
    expect(() => rotationToGcsimActions([])).toThrow(RangeError);
  });

  it("ignore les types inconnus au lieu d'inventer un verbe", () => {
    const out = rotationToGcsimActions([a("Bennett", "skill"), a("Bennett", "teleport")]);
    expect(out).toContain("bennett skill;");
    expect(out).not.toContain("teleport");
  });
});
