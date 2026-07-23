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

/**
 * Injection de faute : enveloppe un PrismaClient pour qu'une transaction
 * interactive exécute TOUT le callback (deleteMany + creates) puis échoue
 * juste AVANT le COMMIT. Prisma doit alors ROLLBACK toute la transaction.
 * On ne teste ainsi que le contrat public ($transaction), pas l'implémentation.
 */
function withRollbackInjection(client: PrismaClient): PrismaClient {
  return new Proxy(client, {
    get(target, prop) {
      if (prop === "$transaction") {
        const original = target.$transaction.bind(target) as unknown as (
          arg: unknown,
          options?: unknown,
        ) => Promise<unknown>;
        return (arg: unknown, options?: unknown) => {
          if (typeof arg === "function") {
            const userFn = arg as (tx: unknown) => Promise<unknown>;
            return original(async (tx: unknown) => {
              await userFn(tx);
              throw new Error("Échec injecté avant COMMIT (test de rollback).");
            }, options);
          }
          // Forme tableau (non utilisée par importTeams) : pass-through.
          return original(arg, options);
        };
      }
      return Reflect.get(target, prop);
    },
  });
}

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

describe("PrismaSqliteTeamRepository.importTeams (transactionnel, remplace-par-nom)", () => {
  it("crée les équipes absentes et rapporte les compteurs", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    const res = await repo.importTeams([
      { name: "imp-counts-a", members: [{ character: "Nahida", slot: 0 }] },
      { name: "imp-counts-b", members: [{ character: "Furina", slot: 0 }] },
    ]);
    expect(res).toEqual({ created: 2, updated: 0 });

    const all = await repo.list();
    expect(all.filter((t) => t.name === "imp-counts-a")).toHaveLength(1);
    expect(all.filter((t) => t.name === "imp-counts-b")).toHaveLength(1);
  });

  it("remplace-par-nom : réimporter compte 'updated', remplace les membres et l'identité", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    const first = await repo.importTeams([
      {
        name: "imp-replace",
        members: [
          { character: "Bennett", slot: 0 },
          { character: "Xiangling", slot: 1 },
        ],
      },
    ]);
    expect(first).toEqual({ created: 1, updated: 0 });
    const before = (await repo.list()).find((t) => t.name === "imp-replace");
    expect(before?.members.map((m) => m.character)).toEqual([
      "Bennett",
      "Xiangling",
    ]);

    const second = await repo.importTeams([
      { name: "imp-replace", members: [{ character: "Mavuika", slot: 0 }] },
      { name: "imp-replace-new", members: [{ character: "Citlali", slot: 0 }] },
    ]);
    expect(second).toEqual({ created: 1, updated: 1 });

    const after = (await repo.list()).find((t) => t.name === "imp-replace");
    expect(after?.members.map((m) => m.character)).toEqual(["Mavuika"]);
    // Remplace-par-nom = supprime puis recrée → nouvelle identité.
    expect(after?.id).not.toBe(before?.id);
    // Aucun doublon de nom après réimport.
    expect(
      (await repo.list()).filter((t) => t.name === "imp-replace"),
    ).toHaveLength(1);
  });

  it("dédoublonne un même nom dans le lot : la DERNIÈRE occurrence gagne", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    const res = await repo.importTeams([
      { name: "imp-dup", members: [{ character: "Ganyu", slot: 0 }] },
      { name: "imp-dup", members: [{ character: "Ayaka", slot: 0 }] },
    ]);
    expect(res).toEqual({ created: 1, updated: 0 });

    const rows = (await repo.list()).filter((t) => t.name === "imp-dup");
    expect(rows).toHaveLength(1);
    expect(rows[0]?.members.map((m) => m.character)).toEqual(["Ayaka"]);
  });

  it("refuse un lot vide ou surdimensionné avant toute écriture", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    await expect(repo.importTeams([])).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
    const tooMany = Array.from({ length: 501 }, () => validTeam());
    await expect(repo.importTeams(tooMany)).rejects.toBeInstanceOf(
      TeamRepositoryValidationError,
    );
  });

  it("fail-fast : un membre invalide dans le lot n'écrit RIEN (aucune écriture partielle)", async () => {
    const repo = new PrismaSqliteTeamRepository(db);
    await repo.save({
      name: "imp-ff-keep",
      members: [{ character: "Kazuha", slot: 0 }],
    });

    await expect(
      repo.importTeams([
        { name: "imp-ff-ok", members: [{ character: "Nilou", slot: 0 }] },
        { name: "imp-ff-bad", members: [{ character: "   ", slot: 0 }] },
      ]),
    ).rejects.toBeInstanceOf(TeamRepositoryValidationError);

    const all = await repo.list();
    // La 1re équipe (valide) du lot ne doit PAS avoir été créée : validation AVANT transaction.
    expect(all.some((t) => t.name === "imp-ff-ok")).toBe(false);
    // L'équipe pré-existante hors lot reste intacte.
    expect(all.some((t) => t.name === "imp-ff-keep")).toBe(true);
  });

  it("rollback : un échec pendant la transaction restaure l'état d'avant (delete-par-nom annulé)", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    // État initial : une équipe visée par l'import (remplace-par-nom) et une hors lot.
    const replace = await repo.save({
      name: "imp-rollback-replace",
      members: [
        { character: "Raiden", slot: 0 },
        { character: "Nahida", slot: 1 },
      ],
    });
    await repo.save({
      name: "imp-rollback-keep",
      members: [{ character: "Yelan", slot: 0 }],
    });

    const failingRepo = new PrismaSqliteTeamRepository(withRollbackInjection(db));
    await expect(
      failingRepo.importTeams([
        { name: "imp-rollback-replace", members: [{ character: "Escoffier", slot: 0 }] },
        { name: "imp-rollback-fresh", members: [{ character: "Kinich", slot: 0 }] },
      ]),
    ).rejects.toThrow();

    const all = await repo.list();
    // 1) Le delete-par-nom a été ANNULÉ : l'équipe visée existe toujours, identité + membres d'origine.
    const stillThere = all.find((t) => t.name === "imp-rollback-replace");
    expect(stillThere?.id).toBe(replace.id);
    expect(stillThere?.members.map((m) => m.character)).toEqual([
      "Raiden",
      "Nahida",
    ]);
    // 2) Les créations ont été annulées : la nouvelle équipe n'existe pas.
    expect(all.some((t) => t.name === "imp-rollback-fresh")).toBe(false);
    // 3) L'équipe hors lot reste intacte.
    expect(all.some((t) => t.name === "imp-rollback-keep")).toBe(true);
  });
});
