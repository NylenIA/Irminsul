import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { PrismaClient } from "@prisma/client";
import { checkSchemaDrift } from "../src/schema-drift";

let db: PrismaClient;
let dir: string;

beforeAll(async () => {
  // Base SQLite jetable et isolée : on n'y applique PAS le schéma applicatif,
  // on pilote directement la table Prisma `_prisma_migrations`.
  dir = mkdtempSync(join(tmpdir(), "irminsul-drift-"));
  process.env["DATABASE_URL"] = `file:${join(dir, "test.db").replaceAll("\\", "/")}`;
  db = new PrismaClient();
  await db.$connect();
});

afterAll(async () => {
  await db?.$disconnect();
  if (dir) rmSync(dir, { recursive: true, force: true });
});

/** Recrée `_prisma_migrations` avec l'état voulu (finished_at NULL = migration non terminée). */
async function setMigrations(
  rows: { name: string; finished: boolean }[],
): Promise<void> {
  await db.$executeRawUnsafe("DROP TABLE IF EXISTS _prisma_migrations");
  await db.$executeRawUnsafe(
    "CREATE TABLE _prisma_migrations (id TEXT PRIMARY KEY, migration_name TEXT NOT NULL, finished_at DATETIME)",
  );
  let i = 0;
  for (const row of rows) {
    i += 1;
    const finished = row.finished ? "CURRENT_TIMESTAMP" : "NULL";
    await db.$executeRawUnsafe(
      `INSERT INTO _prisma_migrations (id, migration_name, finished_at) VALUES ('${i}', '${row.name}', ${finished})`,
    );
  }
}

describe("checkSchemaDrift", () => {
  it("status 'unknown' quand la table _prisma_migrations est absente", async () => {
    await db.$executeRawUnsafe("DROP TABLE IF EXISTS _prisma_migrations");
    const r = await checkSchemaDrift(db, ["a", "b"]);
    expect(r.status).toBe("unknown");
    expect(r.applied).toEqual([]);
    expect(r.expected).toEqual(["a", "b"]);
    expect(r.missing).toEqual([]);
  });

  it("status 'ok' quand toutes les migrations attendues sont appliquées", async () => {
    await setMigrations([
      { name: "a", finished: true },
      { name: "b", finished: true },
    ]);
    const r = await checkSchemaDrift(db, ["b", "a"]);
    expect(r.status).toBe("ok");
    expect(r.applied).toEqual(["a", "b"]);
    expect(r.missing).toEqual([]);
  });

  it("status 'drift' + liste 'missing' quand une migration attendue manque", async () => {
    await setMigrations([{ name: "a", finished: true }]);
    const r = await checkSchemaDrift(db, ["a", "b"]);
    expect(r.status).toBe("drift");
    expect(r.missing).toEqual(["b"]);
    expect(r.detail).toContain("b");
    expect(r.detail.toLowerCase()).toContain("import");
  });

  it("une migration non terminée (finished_at NULL) ne compte pas comme appliquée", async () => {
    await setMigrations([
      { name: "a", finished: true },
      { name: "b", finished: false },
    ]);
    const r = await checkSchemaDrift(db, ["a", "b"]);
    expect(r.status).toBe("drift");
    expect(r.missing).toEqual(["b"]);
  });

  it("des migrations supplémentaires dans la base n'empêchent pas 'ok' (compat ascendante)", async () => {
    await setMigrations([
      { name: "a", finished: true },
      { name: "b", finished: true },
      { name: "c", finished: true },
    ]);
    const r = await checkSchemaDrift(db, ["a", "b"]);
    expect(r.status).toBe("ok");
    expect(r.applied).toEqual(["a", "b", "c"]);
  });
});
