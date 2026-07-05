import { describe, expect, it } from "vitest";
import {
  buildExport,
  checksumOf,
  planImport,
  validateImport,
  EXPORT_FORMAT_VERSION,
  type ExportableTeam,
} from "../src/import-export";

const team = (name: string): ExportableTeam => ({
  name,
  members: [{ character: "Bennett", role: "support", slot: 1 }, { character: "Nahida", role: null, slot: 2 }],
});

describe("buildExport / validateImport (irminsul-export/1.0 — aller-retour, intégrité)", () => {
  it("aller-retour : export puis import redonne les mêmes équipes", () => {
    const file = buildExport([team("B"), team("A")], "1.0.0", new Date("2026-07-04T00:00:00Z"));
    expect(file.formatVersion).toBe(EXPORT_FORMAT_VERSION);
    // Ordre déterministe (nom trié).
    expect(file.data.teams.map((t) => t.name)).toEqual(["A", "B"]);
    const res = validateImport(JSON.stringify(file));
    expect(res.ok).toBe(true);
    if (res.ok) expect(res.file.data.teams).toEqual(file.data.teams);
  });

  it("checksum déterministe et indépendant de l'ordre des clés", () => {
    const a = buildExport([team("X")], "1.0.0", new Date(0));
    const b = buildExport([team("X")], "1.0.0", new Date(0));
    expect(a.checksum).toBe(b.checksum);
    expect(a.checksum).toMatch(/^[0-9a-f]{8}$/);
  });

  it("checksum falsifié → refus (corruption détectée)", () => {
    const file = buildExport([team("X")], "1.0.0");
    const tampered = { ...file, data: { teams: [...file.data.teams, team("Injected")] } };
    const res = validateImport(JSON.stringify(tampered));
    expect(res).toMatchObject({ ok: false, kind: "checksum_mismatch" });
  });

  it("JSON invalide / schéma invalide / version future rejetés proprement", () => {
    expect(validateImport("{ pas du json")).toMatchObject({ ok: false, kind: "invalid_json" });
    expect(validateImport(JSON.stringify({ formatVersion: EXPORT_FORMAT_VERSION, data: { teams: [{ nope: 1 }] } }))).toMatchObject({ ok: false, kind: "invalid_schema" });
    expect(validateImport(JSON.stringify({ formatVersion: "irminsul-export/9.9", data: { teams: [] } }))).toMatchObject({ ok: false, kind: "unsupported_version" });
  });

  it("fichier vide et trop volumineux rejetés", () => {
    expect(validateImport("")).toMatchObject({ ok: false, kind: "invalid_json" });
    expect(validateImport("x".repeat(3 * 1024 * 1024))).toMatchObject({ ok: false, kind: "too_large" });
  });

  it("Unicode préservé dans les noms d'équipe", () => {
    const file = buildExport([team("Équipe 龍 ☂")], "1.0.0");
    const res = validateImport(JSON.stringify(file));
    expect(res.ok).toBe(true);
    if (res.ok) expect(res.file.data.teams[0]!.name).toBe("Équipe 龍 ☂");
  });
});

describe("planImport (aperçu déterministe avant écriture)", () => {
  it("classe created / updated / conflict (doublon interne)", () => {
    const file = buildExport([team("New"), team("Existing")], "1.0.0");
    // Ajoute un doublon interne au fichier.
    file.data.teams.push(team("New"));
    const plan = planImport(file, ["Existing"]);
    expect(plan.created).toBe(1);       // New
    expect(plan.updated).toBe(1);       // Existing
    expect(plan.conflicts).toBe(1);     // doublon New
    expect(plan.total).toBe(3);
    expect(plan.entries.find((e) => e.status === "updated")!.detail).toMatch(/sauvegarde conservée/);
  });
});
