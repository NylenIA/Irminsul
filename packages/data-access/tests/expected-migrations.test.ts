import { describe, expect, it } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { EXPECTED_MIGRATIONS } from "../src/expected-migrations";
import { MIGRATIONS_BUNDLE } from "../src/migrations-bundle";

// Garde-fou : le bundle embarqué (migrations-bundle.ts) doit rester le miroir EXACT
// de `prisma/migrations/` — noms ET contenu SQL. Sinon la détection de dérive et le
// runner de migration deviendraient faux. En cas d'échec : régénérer via
// `node scripts/gen-migrations-bundle.mjs`, et implémenter le runner AVANT d'expédier.
describe("MIGRATIONS_BUNDLE / EXPECTED_MIGRATIONS", () => {
  const migrationsDir = join(process.cwd(), "prisma", "migrations");
  const folderNames = readdirSync(migrationsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();

  it("liste exactement les dossiers de prisma/migrations", () => {
    expect(MIGRATIONS_BUNDLE.map((m) => m.name)).toEqual(folderNames);
    expect([...EXPECTED_MIGRATIONS].sort()).toEqual(folderNames);
  });

  it("embarque le SQL EXACT de chaque migration", () => {
    for (const name of folderNames) {
      const onDisk = readFileSync(join(migrationsDir, name, "migration.sql"), "utf8");
      const bundled = MIGRATIONS_BUNDLE.find((m) => m.name === name);
      expect(bundled, `migration ${name} absente du bundle`).toBeDefined();
      expect(bundled?.sql).toBe(onDisk);
    }
  });
});
