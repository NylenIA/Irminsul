import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { PrismaClient } from "@prisma/client";
import {
  PrismaSqliteTeamRepository,
  TeamRepositoryValidationError,
  type SaveTeamInput,
} from "../src/repositories/team-repository";

let db: PrismaClient;
let dir: string;

async function applySqliteMigrations(client: PrismaClient): Promise<void> {
  const migrationsDir = join(process.cwd(), "prisma", "migrations");
  const migrationNames = readdirSync(migrationsDir)
    .filter((name) => name !== "migration_lock.toml")
    .sort();

  for (const migrationName of migrationNames) {
    const migrationSql = readFileSync(
      join(migrationsDir, migrationName, "migration.sql"),
      "utf8",
    );
    const statements = migrationSql
      .split(/;\s*(?:\r?\n|$)/)
      .map((statement) => statement.trim())
      .filter(Boolean);

    for (const statement of statements) {
      await client.$executeRawUnsafe(statement);
    }
  }
}

function validTeam(overrides: Partial<SaveTeamInput> = {}): SaveTeamInput {
  return {
    name: "Valid team",
    members: [
      { character: "Sandrone", role: "Carry", slot: 0 },
      { character: "Bennett", role: "Buffer", slot: 1 },
    ],
    ...overrides,
  };
}

beforeAll(async () => {
  // Isolated disposable SQLite database for this test run, never dev.db.
  dir = mkdtempSync(join(tmpdir(), "irminsul-da-"));
  const url = `file:${join(dir, "test.db").replaceAll("\\", "/")}`;
  process.env["DATABASE_URL"] = url;
  db = new PrismaClient();
  await applySqliteMigrations(db);
});

afterAll(async () => {
  await db?.$disconnect();
  if (dir) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("PrismaSqliteTeamRepository (local-first)", () => {
  it("saves, reloads and deletes a team", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    const saved = await repo.save({
      name: "Sandrone - Lunar test",
      carry: "Sandrone",
      members: [
        { character: "Sandrone", role: "Carry", slot: 0 },
        { character: "Bennett", role: "Buffer", slot: 1 },
        { character: "Xilonen", role: "Support", slot: 2 },
        { character: "Furina", role: "Support", slot: 3 },
      ],
    });
    expect(saved.id).toBeTruthy();
    expect(saved.members).toHaveLength(4);

    const reloaded = await repo.getById(saved.id);
    expect(reloaded?.name).toBe("Sandrone - Lunar test");
    expect(reloaded?.members.map((m) => m.character)).toEqual([
      "Sandrone",
      "Bennett",
      "Xilonen",
      "Furina",
    ]);

    const list = await repo.list();
    expect(list.some((t) => t.id === saved.id)).toBe(true);

    await repo.delete(saved.id);
    expect(await repo.getById(saved.id)).toBeNull();
  });

  it("normalizes text and reloads members ordered by slot", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    const saved = await repo.save({
      name: "  Trimmed team  ",
      carry: "   ",
      notes: "  Useful notes  ",
      members: [
        { character: "  Furina  ", role: "  Support  ", slot: 2 },
        { character: "  Sandrone  ", role: "   ", slot: 0 },
      ],
    });

    expect(saved.name).toBe("Trimmed team");
    expect(saved.carry).toBeNull();
    expect(saved.notes).toBe("Useful notes");
    expect(saved.members.map((member) => member.slot)).toEqual([0, 2]);
    expect(saved.members[0]).toMatchObject({
      character: "Sandrone",
      role: null,
      slot: 0,
    });
    expect(saved.members[1]).toMatchObject({
      character: "Furina",
      role: "Support",
      slot: 2,
    });
  });

  it("rejects invalid input before Prisma", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    await expect(repo.save(validTeam({ name: "   " }))).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
    await expect(repo.save(validTeam({ members: [] }))).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
    await expect(
      repo.save(
        validTeam({
          members: [
            { character: "A", slot: 0 },
            { character: "B", slot: 1 },
            { character: "C", slot: 2 },
            { character: "D", slot: 3 },
            { character: "E", slot: 4 },
          ],
        }),
      ),
    ).rejects.toBeInstanceOf(TeamRepositoryValidationError);
    await expect(
      repo.save(
        validTeam({
          members: [
            { character: "Sandrone", slot: 0 },
            { character: "Bennett", slot: 0 },
          ],
        }),
      ),
    ).rejects.toBeInstanceOf(TeamRepositoryValidationError);
    await expect(
      repo.save(
        validTeam({
          members: [
            { character: "Sandrone", slot: 0 },
            { character: "Sandrone", slot: 1 },
          ],
        }),
      ),
    ).rejects.toBeInstanceOf(TeamRepositoryValidationError);
    await expect(
      repo.save(validTeam({ members: [{ character: "   ", slot: 0 }] })),
    ).rejects.toBeInstanceOf(TeamRepositoryValidationError);
  });

  it("validates ids and makes delete idempotent", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    await expect(repo.getById("   ")).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
    await expect(repo.delete("   ")).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
    await expect(repo.delete("missing-team-id")).resolves.toBeUndefined();

    const saved = await repo.save(validTeam());
    await expect(repo.delete(saved.id)).resolves.toBeUndefined();
    await expect(repo.delete(saved.id)).resolves.toBeUndefined();
    expect(await repo.getById(saved.id)).toBeNull();
  });

  it("renames and duplicates a team", async () => {
    const repo = new PrismaSqliteTeamRepository(db);
    const saved = await repo.save(validTeam({ name: "Original" }));

    const renamed = await repo.rename(saved.id, "  Renamed  ");
    expect(renamed.name).toBe("Renamed");
    expect((await repo.getById(saved.id))?.name).toBe("Renamed");

    await expect(repo.rename(saved.id, "   ")).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
    await expect(repo.rename("missing-id", "X")).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );

    const copy = await repo.duplicate(saved.id);
    expect(copy.id).not.toBe(saved.id);
    expect(copy.name).toBe("Renamed (copie)");
    expect(copy.members.map((m) => m.character)).toEqual(
      renamed.members.map((m) => m.character),
    );
    await expect(repo.duplicate("missing-id")).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
  });
});
