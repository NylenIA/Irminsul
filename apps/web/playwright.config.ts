import { defineConfig, devices } from "@playwright/test";
import { join } from "node:path";

// Base SQLite ISOLÉE pour les E2E — jamais la dev.db utilisateur.
// Base unique par run (évite tout verrou SQLite résiduel sous Windows).
const DB_FILE = join(process.cwd(), ".e2e", `test-${Date.now()}.db`);
const DATABASE_URL = `file:${DB_FILE.replaceAll("\\", "/")}`;
process.env["DATABASE_URL"] = DATABASE_URL;

const PORT = 3100;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  globalSetup: "./tests/e2e/global-setup.ts",
  use: { baseURL: `http://localhost:${PORT}`, trace: "retain-on-failure" },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } },
    },
    { name: "mobile", use: { ...devices["Pixel 5"] } },
  ],
  webServer: {
    command: `npm run dev -- --port ${PORT}`,
    url: `http://localhost:${PORT}/team-lab`,
    reuseExistingServer: false,
    timeout: 180000,
    env: { DATABASE_URL },
  },
});
