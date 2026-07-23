import { describe, expect, it } from "vitest";
import { readdirSync } from "node:fs";
import { join } from "node:path";
import { EXPECTED_MIGRATIONS } from "../src/expected-migrations";

// Garde-fou : EXPECTED_MIGRATIONS est le miroir embarqué de `prisma/migrations/`.
// S'il diverge (nouvelle migration ajoutée sans mettre la liste à jour), la
// détection de dérive côté desktop deviendrait fausse. Ce test échoue alors,
// rappelant AUSSI d'implémenter le runner de migration avant d'expédier un schéma.
describe("EXPECTED_MIGRATIONS", () => {
  it("liste exactement les dossiers de prisma/migrations", () => {
    const dirs = readdirSync(join(process.cwd(), "prisma", "migrations"), {
      withFileTypes: true,
    })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort();

    expect([...EXPECTED_MIGRATIONS].sort()).toEqual(dirs);
  });
});
