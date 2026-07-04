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

  test("aperçu de coup direct : calcul, provenance, hypothèses, défauts listés", async ({ page }) => {
    await page.getByLabel("Personnage pour l'aperçu").selectOption("Bennett");
    await page.getByPlaceholder("ex. 250").fill("250");
    await page.getByPlaceholder("ex. 2000").fill("2000");
    await page.getByRole("button", { name: "Calculer l'aperçu" }).click();

    // Résultat + libellé honnête (coup isolé, pas un DPS).
    const result = page.getByLabel("Résultat de l'aperçu pour Bennett");
    await expect(result).toBeVisible();
    await expect(result.getByText("Attendu (moyenne crit.)")).toBeVisible();
    // Provenance + confiance visibles.
    await expect(result.getByText("formule vérifiée")).toBeVisible();
    await expect(result.getByText(/contrat direct-hit\//)).toBeVisible();
    await expect(result.getByText(/confiance haute/)).toBeVisible();
    // Défauts utilisés listés (crit/RES/niveaux non renseignés).
    await expect(result.getByText("défauts utilisés")).toBeVisible();
    // Hypothèses dépliables.
    await result.getByText("Hypothèses & provenance").click();
    await expect(result.getByText(/Coup isolé — pas une rotation/)).toBeVisible();
  });

  test("aperçu : données insuffisantes sans rien inventer", async ({ page }) => {
    await page.getByRole("button", { name: "Calculer l'aperçu" }).click();
    await expect(page.getByText("Données insuffisantes")).toBeVisible();
    await expect(page.getByText(/Champs requis : Personnage/)).toBeVisible();
  });

  test("accessibilité (axe) — aucune violation critique/sérieuse", async ({ page }) => {
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id), null, 2)).toEqual([]);
  });
});

test.describe("Pages essentielles (dashboard, personnages, navigation)", () => {
  test("dashboard honnête : comptes réels + contrats moteur + navigation", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Irminsul — Archive astrale" })).toBeVisible();
    await expect(page.getByText(/contrat direct-hit\//)).toBeVisible();
    // Navigation vers Personnages.
    await page.getByRole("navigation").getByRole("link", { name: "Personnages" }).click();
    await expect(page.getByRole("heading", { name: "Personnages" })).toBeVisible();
  });

  test("page personnages : scan réel (provenance) OU état vide honnête", async ({ page }) => {
    await page.goto("/characters");
    const provenance = page.getByText(/personnages scannés/);
    const empty = page.getByText("Aucun scan de compte trouvé");
    await expect(provenance.or(empty)).toBeVisible();
    // Si scan présent : provenance complète affichée.
    if (await provenance.isVisible()) {
      await expect(page.getByText(/source /)).toBeVisible();
      await expect(page.getByText(/confiance /)).toBeVisible();
    }
  });

  test("accessibilité (axe) des nouvelles pages", async ({ page }) => {
    for (const path of ["/", "/characters"]) {
      await page.goto(path);
      const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
      const serious = results.violations.filter(
        (v) => v.impact === "critical" || v.impact === "serious",
      );
      expect(serious, `${path}: ${JSON.stringify(serious.map((v) => v.id))}`).toEqual([]);
    }
  });
});
