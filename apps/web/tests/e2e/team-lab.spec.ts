import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const SLOT_CHARACTERS = ["Bennett", "Xilonen", "Furina", "Nahida"] as const;

async function composeAndSave(page: Page, teamName: string): Promise<void> {
  await page.getByPlaceholder("Ex. Sandrone Lunar-Crystallize").fill(teamName);
  for (let i = 0; i < SLOT_CHARACTERS.length; i++) {
    await page.getByLabel(`Personnage, emplacement ${i + 1}`).selectOption(SLOT_CHARACTERS[i]!);
  }
  await page.getByRole("button", { name: "Sauvegarder l'équipe" }).click();
  await expect(page.getByRole("heading", { name: teamName })).toBeVisible();
}

function teamCard(page: Page, name: string) {
  return page.locator(".irm-card", { hasText: name });
}

async function confirmDelete(page: Page, name: string): Promise<void> {
  await teamCard(page, name).getByRole("button", { name: "Supprimer" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Supprimer" }).click();
  await expect(page.getByRole("heading", { name, exact: true })).toHaveCount(0);
}

test.describe("Laboratoire d'équipes", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/team-lab");
    await expect(page.getByRole("heading", { name: "Laboratoire d'équipes" })).toBeVisible();
  });

  test("rendu initial + état vide", async ({ page }) => {
    await expect(page.getByRole("button", { name: "Sauvegarder l'équipe" })).toBeVisible();
    await expect(page.getByLabel("Personnage, emplacement 1")).toBeVisible();
  });

  test("workflow complet : save, reload, rename, duplicate, delete confirmé", async ({ page }) => {
    const base = `E2E ${Date.now()}`;
    await composeAndSave(page, base);

    // Persistance après reload (vraie base SQLite).
    await page.reload();
    await expect(page.getByRole("heading", { name: base })).toBeVisible();

    // Rename.
    const renamed = `${base} R`;
    await teamCard(page, base).getByRole("button", { name: "Renommer" }).click();
    await page.getByLabel(`Nouveau nom pour ${base}`).fill(renamed);
    await page.getByRole("button", { name: "Valider" }).click();
    await expect(page.getByRole("heading", { name: renamed })).toBeVisible();

    // Duplicate -> "<nom> (copie)".
    await teamCard(page, renamed).getByRole("button", { name: "Dupliquer" }).first().click();
    await expect(page.getByRole("heading", { name: `${renamed} (copie)` })).toBeVisible();

    // Delete avec confirmation (les deux).
    await confirmDelete(page, `${renamed} (copie)`);
    await confirmDelete(page, renamed);
  });

  test("accessibilité (axe) — aucune violation critique/sérieuse", async ({ page }) => {
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id), null, 2)).toEqual([]);
  });
});
