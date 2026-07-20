import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";
import { join } from "node:path";

// Config de smoke versionnée (Bennett seul, 50 itérations) — simulation RÉELLE.
const SMOKE_CONFIG = readFileSync(
  join(process.cwd(), "..", "..", "simulations", "smoke-test.txt"),
  "utf8",
);

test.describe("Simulation gcsim", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/simulation");
    await expect(page.getByRole("heading", { name: "Simulation (gcsim)" })).toBeVisible();
  });

  test("erreur honnête sur configuration vide (aucun DPS inventé)", async ({ page }) => {
    await page.getByRole("button", { name: "Lancer la simulation" }).click();
    await expect(page.getByText("Simulation impossible")).toBeVisible();
    await expect(page.getByText("Configuration vide.")).toBeVisible();
  });

  test("simulation réelle via le binaire local : DPS simulé + libellé SIMULATION", async ({
    page,
  }) => {
    test.setTimeout(150000);
    await page.getByLabel("Configuration gcsim").fill(SMOKE_CONFIG);
    await page.getByRole("button", { name: "Lancer la simulation" }).click();
    await expect(page.getByText("DPS moyen simulé")).toBeVisible({ timeout: 120000 });
    await expect(page.getByText("SIMULATION", { exact: true })).toBeVisible();
    await expect(page.getByText("Durée simulée")).toBeVisible();
  });

  test("accessibilité (axe) de /simulation", async ({ page }) => {
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious).toEqual([]);
  });
});
