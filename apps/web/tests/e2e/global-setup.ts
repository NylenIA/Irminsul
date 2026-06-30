import { execSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";

/** Crée + migre une base SQLite de test isolée (jamais la dev.db utilisateur). */
export default async function globalSetup(): Promise<void> {
  const url = process.env["DATABASE_URL"];
  if (!url || !url.startsWith("file:")) {
    throw new Error("E2E: DATABASE_URL (file:) non défini par playwright.config.ts");
  }
  const file = url.slice("file:".length);
  for (const f of [file, `${file}-journal`]) {
    if (existsSync(f)) rmSync(f, { force: true });
  }
  mkdirSync(dirname(file), { recursive: true });

  // process.cwd() = apps/web (Playwright). data-access = ../../packages/data-access.
  const dataAccess = join(process.cwd(), "..", "..", "packages", "data-access");
  execSync("npx prisma migrate deploy", {
    cwd: dataAccess,
    env: { ...process.env, DATABASE_URL: url },
    stdio: "ignore",
  });
}
