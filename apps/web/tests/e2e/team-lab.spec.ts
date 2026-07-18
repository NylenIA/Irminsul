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

test.describe("Proxy nonce (mode web)", () => {
  test("POST applicatif non authentifié n'est pas rejeté en 403 sans IRMINSUL_NONCE", async ({ request }) => {
    // En E2E web, Tauri ne pose pas IRMINSUL_NONCE : le proxy doit rester inactif.
    // Le refus 403 desktop est couvert uniquement par scripts/smoke-desktop.mjs.
    const response = await request.post("/", { data: "mutation-probe" });
    expect(response.status()).not.toBe(403);
  });
});

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
    // Provenance + confiance visibles. Le moteur PAR DÉFAUT est le sidecar Python
    // réel (repli TS uniquement si Python indisponible → ce test échouerait, voulu).
    await expect(result.getByText("moteur python-sidecar")).toBeVisible();
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

test.describe("Détail personnage — stats finales (moteur Python via sidecar)", () => {
  test("affiche les stats finales OU un état d'échec honnête, avec provenance/hypothèses", async ({ page }) => {
    // Mavuika est dans le scan de référence ; si le sidecar est indisponible → état d'erreur typé.
    await page.goto("/characters/Mavuika");
    await expect(page.getByRole("heading", { name: "Mavuika" })).toBeVisible();

    const statsView = page.getByLabel("Stats finales de Mavuika");
    const engineError = page.getByText("Erreur du moteur");
    const noScan = page.getByText("Aucun scan de compte");
    await expect(statsView.or(engineError).or(noScan)).toBeVisible({ timeout: 15000 });

    // Chemin nominal : breakdown + confiance + provenance visibles ; jamais NaN/Infinity.
    if (await statsView.isVisible()) {
      await expect(statsView.getByText("ATQ")).toBeVisible();
      await expect(statsView.getByText(/confiance (haute|moyenne|faible)/)).toBeVisible();
      await expect(statsView).not.toContainText("NaN");
      await expect(statsView).not.toContainText("Infinity");
      await page.getByText("Hypothèses & provenance").click();
      await expect(page.getByText(/SANS buffs conditionnels/)).toBeVisible();
    }
  });

  test("accessibilité (axe) du détail personnage", async ({ page }) => {
    await page.goto("/characters/Mavuika");
    await expect(page.getByRole("heading", { name: "Mavuika" })).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
  });
});

test.describe("Rotations — moteur chiffré (jamais de faux DPS)", () => {
  test("calcule une rotation depuis une équipe sauvegardée, DPS seulement si complet", async ({ page }) => {
    // Prépare une équipe avec Bennett (présent dans scan+talent+base).
    await page.goto("/team-lab");
    const teamName = `Rota ${Date.now()}`;
    await page.getByPlaceholder("Ex. Sandrone Lunar-Crystallize").fill(teamName);
    await page.getByLabel("Personnage, emplacement 1").selectOption("Bennett");
    await page.getByRole("button", { name: "Sauvegarder l'équipe" }).click();
    await expect(page.getByRole("heading", { name: teamName })).toBeVisible();

    await page.goto("/rotations");
    await expect(page.getByRole("heading", { name: "Rotations" })).toBeVisible();
    await page.getByLabel("Équipe sauvegardée").selectOption({ label: teamName });

    // Ajoute une attaque normale (talent par défaut combat1 / 1-Hit DMG / 10) et calcule.
    await page.getByRole("button", { name: "+ Action" }).click();
    await page.getByRole("button", { name: "Calculer la rotation" }).click();

    const result = page.getByLabel("Résultat de la rotation");
    await expect(result).toBeVisible({ timeout: 15000 });
    await expect(result.getByText(/contrat rotation\//)).toBeVisible();
    // Jamais NaN/Infinity affichés.
    await expect(result).not.toContainText("NaN");
    await expect(result).not.toContainText("Infinity");
    await result.getByText("Hypothèses & provenance").click();
    await expect(result.getByText(/coefficient de talent réel/)).toBeVisible();
  });

  test("accessibilité (axe) de /rotations", async ({ page }) => {
    await page.goto("/rotations");
    await expect(page.getByRole("heading", { name: "Rotations" })).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
  });
});

test.describe("Comparateur quantitatif (team-compare/1.0)", () => {
  test("compare deux équipes sur deux rotations + cible commune ; verdict sourcé", async ({ page }) => {
    // Deux équipes distinctes (Mavuika a une ATQ finale complète → rotation complète possible).
    for (const [name, char] of [["Cmp A", "Mavuika"], ["Cmp B", "Bennett"]] as const) {
      await page.goto("/team-lab");
      await page.getByPlaceholder("Ex. Sandrone Lunar-Crystallize").fill(`${name} ${Date.now()}`);
      await page.getByLabel("Personnage, emplacement 1").selectOption(char);
      await page.getByRole("button", { name: "Sauvegarder l'équipe" }).click();
      await expect(page.getByRole("heading", { name: new RegExp(name) })).toBeVisible();
    }

    await page.goto("/team-compare");
    await expect(page.getByRole("heading", { name: "Comparateur d'équipes" })).toBeVisible();
    const empty = page.getByText("Il faut au moins deux équipes");
    if (await empty.isVisible().catch(() => false)) return;

    // Ajoute une action à chaque côté puis compare.
    const addButtons = page.getByRole("button", { name: "+ Action" });
    await addButtons.nth(0).click();
    await addButtons.nth(1).click();
    await page.getByRole("button", { name: "Comparer quantitativement" }).click();

    const result = page.getByLabel("Résultat de la comparaison");
    await expect(result).toBeVisible({ timeout: 15000 });
    await expect(result.getByText(/contrat team-compare\//)).toBeVisible();
    // Jamais de NaN/Infinity ; un verdict (complet) ou message d'insuffisance (honnête).
    await expect(result).not.toContainText("NaN");
    await expect(result).not.toContainText("Infinity");
    await expect(result.getByText(/DPS moyen/).first()).toBeVisible();
  });

  test("accessibilité (axe) de /team-compare", async ({ page }) => {
    await page.goto("/team-compare");
    await expect(page.getByRole("heading", { name: "Comparateur d'équipes" })).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
  });
});

test.describe("Recommandations transparentes (recommendations/1.0)", () => {
  test("analyse qualité des données : preuves, confiance, provenance ; jamais d'impact chiffré", async ({ page }) => {
    await page.goto("/recommendations");
    await expect(page.getByRole("heading", { name: "Recommandations" })).toBeVisible();
    await page.getByLabel("Objectif").selectOption("data_quality");
    await page.getByRole("button", { name: "Analyser" }).click();

    const section = page.getByLabel("Recommandations");
    await expect(section).toBeVisible({ timeout: 15000 });
    await expect(section.getByText(/contrat recommendations\//)).toBeVisible();
    await expect(section.getByText(/confiance /).first()).toBeVisible();
    // Aucun impact chiffré fabriqué : les impacts sont qualitatifs.
    await expect(section).not.toContainText("DPS +");
  });

  test("objectif non modélisé → recommandation qualitative honnête", async ({ page }) => {
    await page.goto("/recommendations");
    await page.getByLabel("Objectif").selectOption("survivability");
    await page.getByRole("button", { name: "Analyser" }).click();
    const section = page.getByLabel("Recommandations");
    await expect(section.getByText(/qualitative uniquement/)).toBeVisible({ timeout: 15000 });
  });

  test("accessibilité (axe) de /recommendations", async ({ page }) => {
    await page.goto("/recommendations");
    await expect(page.getByRole("heading", { name: "Recommandations" })).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
  });
});

test.describe("Import / Export (irminsul-export/1.0)", () => {
  test("aller-retour : export d'une équipe puis réimport avec aperçu transactionnel", async ({ page }) => {
    // Crée une équipe à exporter.
    const teamName = `IO ${Date.now()}`;
    await page.goto("/team-lab");
    await page.getByPlaceholder("Ex. Sandrone Lunar-Crystallize").fill(teamName);
    await page.getByLabel("Personnage, emplacement 1").selectOption("Bennett");
    await page.getByRole("button", { name: "Sauvegarder l'équipe" }).click();
    await expect(page.getByRole("heading", { name: teamName })).toBeVisible();

    // Export → capture le téléchargement.
    await page.goto("/import-export");
    await expect(page.getByRole("heading", { name: "Import / Export" })).toBeVisible();
    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Exporter mes équipes" }).click();
    const download = await downloadPromise;
    const path = await download.path();
    expect(path).toBeTruthy();

    // Réimport du fichier → aperçu (l'équipe existe déjà → "à remplacer").
    await page.getByLabel("Fichier d'import").setInputFiles(path!);
    const preview = page.getByLabel("Aperçu de l'import");
    await expect(preview).toBeVisible({ timeout: 15000 });
    await expect(preview.getByText(/à remplacer/)).toBeVisible();
    // Applique l'import (transactionnel).
    await page.getByRole("button", { name: "Appliquer l'import" }).click();
    await expect(page.getByText("Import réussi")).toBeVisible({ timeout: 15000 });
  });

  test("import d'un JSON invalide → erreur actionnable, aucune écriture", async ({ page }) => {
    await page.goto("/import-export");
    // Injecte un fichier invalide via un DataTransfer simulé.
    await page.getByLabel("Fichier d'import").setInputFiles({
      name: "bad.json", mimeType: "application/json", buffer: Buffer.from("{ pas du json"),
    });
    await expect(page.getByText("Import impossible")).toBeVisible({ timeout: 15000 });
  });

  test("diagnostic : provenance moteur réelle, rapport sanitizé, mode web indiqué", async ({ page }) => {
    await page.goto("/diagnostic");
    await expect(page.getByRole("heading", { name: "Diagnostic" })).toBeVisible();
    await expect(page.getByText("mode web", { exact: true })).toBeVisible();
    // Provenance réelle (moteur source en E2E web) OU erreur honnête — jamais une fenêtre vide.
    const contract = page.getByText("engine-ipc/1.0");
    const engineError = page.getByText(/Moteur injoignable/);
    await expect(contract.or(engineError)).toBeVisible({ timeout: 15000 });
    // Sanitization : le nom du compte utilisateur ne doit pas apparaître dans la page.
    await expect(page.locator("body")).not.toContainText("akuon");
    await expect(page.getByRole("button", { name: /Copier le rapport/ })).toBeVisible();
  });

  test("accessibilité (axe) de /diagnostic", async ({ page }) => {
    await page.goto("/diagnostic");
    await expect(page.getByRole("heading", { name: "Diagnostic" })).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
  });

  test("accessibilité (axe) de /import-export", async ({ page }) => {
    await page.goto("/import-export");
    await expect(page.getByRole("heading", { name: "Import / Export" })).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(serious, JSON.stringify(serious.map((v) => v.id))).toEqual([]);
  });
});

test.describe("Aperçu de coup — réaction lunaire", () => {
  test("le sélecteur de réaction propose lunaires (LC + LCrys) et additives", async ({ page }) => {
    await page.goto("/team-lab");
    const select = page.getByLabel("Réaction élémentaire");
    await expect(select.locator('option[value="lunar-charged"]')).toHaveCount(1);
    await expect(select.locator('option[value="lunar-crystallize"]')).toHaveCount(1);
    await expect(select.locator('option[value="aggravate"]')).toHaveCount(1);
    await expect(select.locator('option[value="spread"]')).toHaveCount(1);
  });
});
