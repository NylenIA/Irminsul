// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { Button } from "../src/components/Button";
import { Input } from "../src/components/Input";
import { Select } from "../src/components/Select";
import { EmptyState, ErrorState, LoadingState } from "../src/components/States";
import { ConfirmDialog } from "../src/components/ConfirmDialog";

// Rendu jsdom des primitives du design system : jusqu'ici couvertes seulement
// en E2E. On teste la LOGIQUE de rendu (mapping variante -> classe, fusion de
// className, passe-plat des props natives, rôles a11y) et le câblage des actions.
afterEach(cleanup);

// jsdom (v26) n'implémente pas <dialog>.showModal()/close(). On les polyfille
// pour tester le composant : ils reflètent l'attribut `open`, ce qui rend le
// contenu du dialog accessible (un dialog fermé est inaccessible par contrat
// ARIA). En prod et en E2E (Chromium), le navigateur fournit les vraies API.
if (typeof HTMLDialogElement !== "undefined") {
  if (!HTMLDialogElement.prototype.showModal) {
    HTMLDialogElement.prototype.showModal = function showModal(
      this: HTMLDialogElement,
    ): void {
      this.open = true;
    };
  }
  if (!HTMLDialogElement.prototype.close) {
    HTMLDialogElement.prototype.close = function close(
      this: HTMLDialogElement,
    ): void {
      this.open = false;
    };
  }
}

describe("Button", () => {
  it("mappe la variante sur la bonne classe et est de type button par défaut", () => {
    render(<Button variant="danger">Supprimer</Button>);
    const btn = screen.getByRole("button", { name: "Supprimer" });
    expect(btn.className).toBe("irm-btn irm-btn--danger");
    expect(btn.getAttribute("type")).toBe("button");
  });

  it("utilise la classe par défaut sans variante", () => {
    render(<Button>OK</Button>);
    expect(screen.getByRole("button", { name: "OK" }).className).toBe("irm-btn");
  });

  it("fusionne la className fournie et déclenche onClick", () => {
    const onClick = vi.fn();
    render(
      <Button variant="primary" className="w-full" onClick={onClick}>
        Valider
      </Button>,
    );
    const btn = screen.getByRole("button", { name: "Valider" });
    expect(btn.className).toBe("irm-btn irm-btn--primary w-full");
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("transmet les props natives (disabled, aria-label, type)", () => {
    render(
      <Button disabled type="submit" aria-label="Envoyer le formulaire">
        →
      </Button>,
    );
    const btn = screen.getByRole("button", { name: "Envoyer le formulaire" });
    expect(btn).toHaveProperty("disabled", true);
    expect(btn.getAttribute("type")).toBe("submit");
  });
});

describe("Input", () => {
  it("applique la classe de base et transmet les props natives", () => {
    render(<Input placeholder="Nom d'équipe" defaultValue="Mavuika" />);
    const input = screen.getByPlaceholderText("Nom d'équipe") as HTMLInputElement;
    expect(input.className).toBe("irm-input");
    expect(input.value).toBe("Mavuika");
  });

  it("fusionne une className additionnelle", () => {
    render(<Input aria-label="recherche" className="grow" />);
    expect(screen.getByLabelText("recherche").className).toBe("irm-input grow");
  });
});

describe("Select", () => {
  it("compose la classe base (irm-input irm-select) et réagit au changement", () => {
    const onChange = vi.fn();
    render(
      <Select aria-label="carry" defaultValue="a" onChange={onChange}>
        <option value="a">A</option>
        <option value="b">B</option>
      </Select>,
    );
    const select = screen.getByLabelText("carry") as HTMLSelectElement;
    expect(select.className).toBe("irm-input irm-select");
    fireEvent.change(select, { target: { value: "b" } });
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(select.value).toBe("b");
  });

  it("fusionne une className additionnelle", () => {
    render(
      <Select aria-label="s" className="w-40">
        <option value="a">A</option>
      </Select>,
    );
    expect(screen.getByLabelText("s").className).toBe("irm-input irm-select w-40");
  });
});

describe("États (Empty / Loading / Error)", () => {
  it("EmptyState : rôle status, titre et contenu", () => {
    render(
      <EmptyState title="Aucune équipe">Crée ta première équipe.</EmptyState>,
    );
    const el = screen.getByRole("status");
    expect(el.textContent).toContain("Aucune équipe");
    expect(el.textContent).toContain("Crée ta première équipe.");
  });

  it("LoadingState : rôle status, aria-live polite et libellé par défaut", () => {
    render(<LoadingState />);
    const el = screen.getByRole("status");
    expect(el.getAttribute("aria-live")).toBe("polite");
    expect(el.textContent).toContain("Chargement…");
  });

  it("LoadingState : libellé personnalisé", () => {
    render(<LoadingState label="Import en cours…" />);
    expect(screen.getByRole("status").textContent).toContain("Import en cours…");
  });

  it("ErrorState : rôle alert, titre et remède", () => {
    render(
      <ErrorState title="Échec de l'import">Vérifie le fichier JSON.</ErrorState>,
    );
    const el = screen.getByRole("alert");
    expect(el.className).toContain("irm-state--error");
    expect(el.textContent).toContain("Échec de l'import");
    expect(el.textContent).toContain("Vérifie le fichier JSON.");
  });
});

describe("ConfirmDialog", () => {
  it("câble les actions et rend le message conditionnellement (dialog ouvert)", () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(
      <ConfirmDialog
        open
        title="Supprimer l'équipe ?"
        message="Action définitive."
        onConfirm={onConfirm}
        onCancel={onCancel}
      />,
    );
    expect(
      screen.getByRole("heading", { name: "Supprimer l'équipe ?" }),
    ).toBeTruthy();
    expect(screen.getByText("Action définitive.")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Confirmer" }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button", { name: "Annuler" }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("n'affiche pas de message quand il est absent", () => {
    render(
      <ConfirmDialog open title="Titre seul" onConfirm={() => {}} onCancel={() => {}} />,
    );
    expect(document.querySelector(".irm-dialog__msg")).toBeNull();
  });

  it("utilise des libellés par défaut personnalisables (dialog ouvert)", () => {
    render(
      <ConfirmDialog
        open
        title="T"
        confirmLabel="Écraser"
        cancelLabel="Garder"
        onConfirm={() => {}}
        onCancel={() => {}}
      />,
    );
    expect(screen.getByRole("button", { name: "Écraser" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Garder" })).toBeTruthy();
  });

  it("ouvre le dialog modal quand open=true et le referme quand open=false", () => {
    const { container, rerender } = render(
      <ConfirmDialog open title="T" onConfirm={() => {}} onCancel={() => {}} />,
    );
    const dialog = container.querySelector("dialog") as HTMLDialogElement;
    expect(dialog.open).toBe(true);

    rerender(
      <ConfirmDialog open={false} title="T" onConfirm={() => {}} onCancel={() => {}} />,
    );
    expect(dialog.open).toBe(false);
  });
});
