import { execSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

async function removeTestDbFile(file: string): Promise<void> {
  for (let attempt = 0; attempt <= 20; attempt++) {
    try {
      rmSync(file, { force: true, maxRetries: 10, retryDelay: 100 });
      return;
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if ((code !== "EPERM" && code !== "EBUSY") || attempt === 20) {
        if ((code === "EPERM" || code === "EBUSY") && existsSync(file) && statSync(file).size === 0) return;
        throw error;
      }
      await delay(250);
    }
  }
}

/** Crée + migre une base SQLite de test isolée (jamais la dev.db utilisateur). */
export default async function globalSetup(): Promise<void> {
  const url = process.env["DATABASE_URL"];
  if (!url || !url.startsWith("file:")) {
    throw new Error("E2E: DATABASE_URL (file:) non défini par playwright.config.ts");
  }
  const file = url.slice("file:".length);
  for (const f of [file, `${file}-journal`]) {
    if (existsSync(f)) await removeTestDbFile(f);
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
