import { expect, test } from "@playwright/test";
import { join } from "node:path";

// Spec exécutée en ESM : pas de __dirname — cwd Playwright = apps/web.
const FIXTURES = join(process.cwd(), "tests", "e2e", "fixtures");

/**
 * Import du compte DANS l'app (le correctif du « rien ne fonctionne » desktop) :
 * environnement de données ISOLÉ (IRMINSUL_DATA_DIR, cf. playwright.config) →
 * on reproduit la réalité d'un utilisateur frais, puis on importe un vrai
 * fichier GOOD via l'UI et le roster apparaît. Aucune commande CLI.
 */
test.describe("Import de compte dans l'app (GOOD)", () => {
  test("fichier invalide → erreur honnête, aucune donnée créée", async ({ page }) => {
    await page.goto("/characters");
    // L'app propose l'import (état vide actionnable) OU le roster existe déjà
    // (2e projet Playwright après le 1er import) — dans ce cas le ré-import est repliable.
    const freshForm = page.getByRole("heading", { name: /Commence ici/ });
    if (!(await freshForm.isVisible().catch(() => false))) {
      await page.locator("summary", { hasText: "Mettre à jour le scan" }).click();
    }
    const input = page.getByLabel("Fichier de scan GOOD (.json)").first();
    await input.setInputFiles({
      name: "pas-un-good.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify({ format: "NOPE" })),
    });
    await page.getByRole("button", { name: /Importer mon compte|Mettre à jour le scan/ }).first().click();
    // Filtré par texte : l'announcer de route Next porte aussi role=alert (vide).
    await expect(page.getByRole("alert").filter({ hasText: /GOOD/ })).toBeVisible();
  });

  test("import d'un GOOD valide via l'UI → le roster apparaît", async ({ page }) => {
    await page.goto("/characters");
    const freshForm = page.getByRole("heading", { name: /Commence ici/ });
    if (!(await freshForm.isVisible().catch(() => false))) {
      await page.locator("summary", { hasText: "Mettre à jour le scan" }).click();
    }
    const input = page.getByLabel("Fichier de scan GOOD (.json)").first();
    await input.setInputFiles(join(FIXTURES, "good-mini.json"));
    await page.getByRole("button", { name: /Importer mon compte|Mettre à jour le scan/ }).first().click();

    // Le roster réel apparaît sans recharger à la main (router.refresh).
    await expect(page.getByText("2 personnages scannés")).toBeVisible({ timeout: 20000 });
    await expect(page.getByRole("link", { name: /Furina/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /Nahida/ })).toBeVisible();
  });
});
