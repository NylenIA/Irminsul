import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { execSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { PrismaClient } from "@prisma/client";
import { PrismaSqliteTeamRepository } from "../src/repositories/team-repository";

let db: PrismaClient;
let dir: string;

beforeAll(() => {
  // Base SQLite isolée et jetable par run de test (jamais la dev.db).
  dir = mkdtempSync(join(tmpdir(), "irminsul-da-"));
  const url = `file:${join(dir, "test.db")}`;
  process.env["DATABASE_URL"] = url;
  execSync("npx prisma migrate deploy", {
    env: { ...process.env, DATABASE_URL: url },
    stdio: "ignore",
  });
  db = new PrismaClient();
});

afterAll(async () => {
  await db.$disconnect();
  rmSync(dir, { recursive: true, force: true });
});

describe("PrismaSqliteTeamRepository (local-first)", () => {
  it("sauvegarde, recharge puis supprime une équipe", async () => {
    const repo = new PrismaSqliteTeamRepository(db);

    const saved = await repo.save({
      name: "Sandrone — Lunar test",
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
    expect(reloaded?.name).toBe("Sandrone — Lunar test");
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
});
