import { describe, expect, it } from "vitest";
import { normalizeFinalStats, FINAL_STATS_CONTRACT_VERSION } from "../src/final-stats";

// Payload réel (forme) produit par charstats.character_payload — Mavuika C0 complète.
const COMPLETE = {
  status: "ok",
  character: {
    key: "Mavuika",
    level: 90,
    ascension: 6,
    constellation: 0,
    final_stats: {
      complete: true,
      note: "Stats finales = écran du jeu (hors buffs conditionnels).",
      hp: { value: 21072.57, complete: true, missing: [] },
      atk: { value: 2377.52, complete: true, missing: [] },
      def: { value: 843.86, complete: true, missing: [] },
      crit_rate_: { value: 22.8, complete: true, missing: [] },
      crit_dmg_: { value: 198.0, complete: true, missing: [] },
      eleMas: { value: 124.0, complete: true, missing: [] },
      enerRech_: { value: 122.0, complete: true, missing: [] },
      dmg_bonus: { pyro_dmg_: 46.6 },
      weapon: {
        supported: true, valid: true, key: "WolfsGravestone",
        base_atk: 532.23, secondary_stat_key: "atk_", secondary_stat_value: 45.252,
      },
    },
    provenance: { snapshot_date: "2026-06-26", source: "Inventory_Kamera", sha256: "f42d", good_version: 3 },
  },
};

describe("normalizeFinalStats (adapter pur — confiance dérivée de la complétude réelle)", () => {
  it("build complet → confiance haute, cellules complètes, provenance sûre", () => {
    const res = normalizeFinalStats(COMPLETE);
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    const s = res.stats;
    expect(s.complete).toBe(true);
    expect(s.confidence).toBe("high");
    expect(s.atk.value).toBe(2377.52);
    expect(s.atk.complete).toBe(true);
    expect(s.damageBonuses["pyro_dmg_"]).toBe(46.6);
    expect(s.weapon.key).toBe("WolfsGravestone");
    expect(s.warnings).toEqual([]);
    expect(s.contractVersion).toBe(FINAL_STATS_CONTRACT_VERSION);
    // Provenance : jamais de chemin local.
    expect(JSON.stringify(s.provenance)).not.toMatch(/[A-Za-z]:\\|source_path|Bureau/);
    expect(s.provenance.source).toBe("Inventory_Kamera");
  });

  it("build partiel (arme non supportée) → confiance moyenne + warnings listés, jamais de 0 inventé", () => {
    const partial = structuredClone(COMPLETE);
    partial.character.final_stats.complete = false;
    partial.character.final_stats.atk = {
      value: 1800, complete: false, missing: ["arme non prise en charge (ATQ de base inconnue)"],
    } as never;
    const res = normalizeFinalStats(partial);
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    expect(res.stats.complete).toBe(false);
    expect(res.stats.confidence).toBe("medium");
    expect(res.stats.atk.complete).toBe(false);
    expect(res.stats.warnings.join(" ")).toMatch(/arme non prise en charge/);
  });

  it("valeur non finie rejetée → cellule value=null (jamais NaN/Infinity affiché)", () => {
    const bad = structuredClone(COMPLETE);
    bad.character.final_stats.hp = { value: null, complete: false, missing: ["valeur non finie rejetée"] } as never;
    const res = normalizeFinalStats(bad);
    expect(res.ok).toBe(true);
    if (!res.ok) return;
    expect(res.stats.hp.value).toBeNull();
    expect(res.stats.hp.complete).toBe(false);
  });

  it("états d'échec : empty / not_found / unsupported", () => {
    expect(normalizeFinalStats({ status: "empty" })).toMatchObject({ ok: false, kind: "empty" });
    expect(normalizeFinalStats({ status: "ok", character: {} })).toMatchObject({ ok: false, kind: "not_found" });
    expect(
      normalizeFinalStats({ status: "ok", character: { key: "Zibai" } }),
    ).toMatchObject({ ok: false, kind: "unsupported" });
  });
});
