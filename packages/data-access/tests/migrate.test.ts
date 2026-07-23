import { afterEach, describe, expect, it } from "vitest";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { PrismaClient } from "@prisma/client";
import { applyPendingMigrations } from "../src/migrate";
import { MIGRATIONS_BUNDLE, type BundledMigration } from "../src/migrations-bundle";

interface Fixture {
  db: PrismaClient;
  cleanup: () => Promise<void>;
}

const fixtures: Fixture[] = [];

/** Base SQLite jetable et isolée pour un test (jamais dev.db). */
async function freshDb(): Promise<PrismaClient> {
  const dir = mkdtempSync(join(tmpdir(), "irminsul-migrate-"));
  process.env["DATABASE_URL"] = `file:${join(dir, "test.db").replaceAll("\\", "/")}`;
  const db = new PrismaClient();
  await db.$connect();
  fixtures.push({
    db,
    cleanup: async () => {
      await db.$disconnect();
      rmSync(dir, { recursive: true, force: true });
    },
  });
  return db;
}

/** Table `_prisma_migrations` au schéma réel de Prisma (base "gérée", vide). */
async function createManagedDb(db: PrismaClient): Promise<void> {
  await db.$executeRawUnsafe(`CREATE TABLE "_prisma_migrations" (
    "id" TEXT PRIMARY KEY NOT NULL,
    "checksum" TEXT NOT NULL,
    "finished_at" DATETIME,
    "migration_name" TEXT NOT NULL,
    "logs" TEXT,
    "rolled_back_at" DATETIME,
    "started_at" DATETIME NOT NULL DEFAULT current_timestamp,
    "applied_steps_count" INTEGER NOT NULL DEFAULT 0
  )`);
}

const INIT = "20260630045245_init_local_app_data";

afterEach(async () => {
  while (fixtures.length) await fixtures.pop()?.cleanup();
});

describe("applyPendingMigrations", () => {
  it("applique la migration init sur une base gérée vide, puis est idempotent", async () => {
    const db = await freshDb();
    await createManagedDb(db);

    const first = await applyPendingMigrations(db, MIGRATIONS_BUNDLE);
    expect(first.status).toBe("applied");
    expect(first.applied).toEqual([INIT]);

    // Les tables applicatives existent désormais (aucune erreur).
    const rows = await db.$queryRawUnsafe<{ n: number }[]>(`SELECT COUNT(*) AS n FROM "SavedTeam"`);
    expect(Number(rows[0]?.n)).toBe(0);

    // Enregistrée dans _prisma_migrations.
    const rec = await db.$queryRawUnsafe<{ migration_name: string }[]>(
      "SELECT migration_name FROM _prisma_migrations WHERE finished_at IS NOT NULL",
    );
    expect(rec.map((r) => r.migration_name)).toContain(INIT);

    // 2e passage : rien à faire.
    const second = await applyPendingMigrations(db, MIGRATIONS_BUNDLE);
    expect(second.status).toBe("noop");
    expect(second.applied).toEqual([]);
  });

  it("ne touche PAS une base non gérée par Prisma (_prisma_migrations absent)", async () => {
    const db = await freshDb();
    const res = await applyPendingMigrations(db, MIGRATIONS_BUNDLE);
    expect(res.status).toBe("skipped-unmanaged");
    // Aucune table applicative créée.
    await expect(
      db.$queryRawUnsafe(`SELECT 1 FROM "SavedTeam"`),
    ).rejects.toThrow();
  });

  it("applique une NOUVELLE migration en préservant les données existantes", async () => {
    const db = await freshDb();
    await createManagedDb(db);
    await applyPendingMigrations(db, MIGRATIONS_BUNDLE);

    // Donnée utilisateur existante.
    await db.$executeRawUnsafe(
      `INSERT INTO "SavedTeam" ("id", "name", "updatedAt") VALUES ('t1', 'À garder', CURRENT_TIMESTAMP)`,
    );

    // Bundle simulant une 2e version (migration additive).
    const bundle: BundledMigration[] = [
      ...MIGRATIONS_BUNDLE,
      { name: "20990101000000_add_column", sql: `ALTER TABLE "SavedTeam" ADD COLUMN "extra" TEXT;\n` },
    ];
    const res = await applyPendingMigrations(db, bundle);
    expect(res.status).toBe("applied");
    expect(res.applied).toEqual(["20990101000000_add_column"]);

    // Données préservées + nouvelle colonne utilisable.
    const rows = await db.$queryRawUnsafe<{ name: string }[]>(`SELECT "name" FROM "SavedTeam"`);
    expect(rows.map((r) => r.name)).toEqual(["À garder"]);
    await db.$executeRawUnsafe(`UPDATE "SavedTeam" SET "extra" = 'ok' WHERE "id" = 't1'`);
  });

  it("rollback : une migration invalide n'est pas enregistrée et préserve l'état", async () => {
    const db = await freshDb();
    await createManagedDb(db);
    await applyPendingMigrations(db, MIGRATIONS_BUNDLE);
    await db.$executeRawUnsafe(
      `INSERT INTO "SavedTeam" ("id", "name", "updatedAt") VALUES ('t1', 'À garder', CURRENT_TIMESTAMP)`,
    );

    const bundle: BundledMigration[] = [
      ...MIGRATIONS_BUNDLE,
      { name: "20990101000001_broken", sql: `CECI N'EST PAS DU SQL;\n` },
    ];
    await expect(applyPendingMigrations(db, bundle)).rejects.toThrow();

    // La migration cassée n'est PAS enregistrée.
    const rec = await db.$queryRawUnsafe<{ migration_name: string }[]>(
      "SELECT migration_name FROM _prisma_migrations WHERE finished_at IS NOT NULL",
    );
    expect(rec.map((r) => r.migration_name)).not.toContain("20990101000001_broken");
    // Donnée préexistante intacte.
    const rows = await db.$queryRawUnsafe<{ name: string }[]>(`SELECT "name" FROM "SavedTeam"`);
    expect(rows.map((r) => r.name)).toEqual(["À garder"]);
  });
});
