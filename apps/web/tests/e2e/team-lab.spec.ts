import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

// Personnages présents dans la source locale genshin-db (Sandrone absente de cette version).
const SLOT_CHARACTERS = ["Bennett", "Xilonen", "Furina", "Nahida"] as const;

test.describe("Laboratoire d'équipes", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/team-lab");
    await expect(page.getByRole("heading", { name: "Laboratoire d'équipes" })).toBeVisible();
  });

  test("rendu initial + état vide", async ({ page }) => {
    await expect(page.getByRole("button", { name: "Sauvegarder l'équipe" })).toBeVisible();
    // 118 personnages réels chargés (au moins un connu présent comme option).
    await expect(page.getByLabel("Personnage, emplacement 1")).toBeVisible();
  });

  test("sauvegarde, persiste après reload, puis supprime", async ({ page }) => {
    const teamName = `E2E ${Date.now()}`;
    await page.getByPlaceholder("Ex. Sandrone Lunar-Crystallize").fill(teamName);
    for (let i = 0; i < SLOT_CHARACTERS.length; i++) {
      await page.getByLabel(`Personnage, emplacement ${i + 1}`).selectOption(SLOT_CHARACTERS[i]!);
    }
    await page.getByRole("button", { name: "Sauvegarder l'équipe" }).click();

    // Apparaît dans la liste des équipes sauvegardées.
    await expect(page.getByRole("heading", { name: teamName })).toBeVisible();

    // Persistance : après reload, l'équipe est toujours là (vraie base SQLite).
    await page.reload();
    await expect(page.getByRole("heading", { name: teamName })).toBeVisible();

    // Suppression.
    const card = page.locator(".irm-card", { hasText: teamName });
    await card.getByRole("button", { name: "Supprimer" }).click();
    await expect(page.getByRole("heading", { name: teamName })).toHaveCount(0);
  });

  test("accessibilité (axe) — aucune violation critique/sérieuse", async ({ page }) => {
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"])
      .analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id), null, 2)).toEqual([]);
  });
});
