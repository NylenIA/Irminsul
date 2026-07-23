// @vitest-environment jsdom
import { afterEach, describe, expect, it } from "vitest";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { Card } from "../src/components/Card";
import {
  Toaster,
  toast,
  subscribeToasts,
  dismissToast,
} from "../src/components/Toast";

// Le store Toast est module-level : on le purge entre les tests pour éviter
// qu'un toast d'un test fuite dans le suivant (le nouveau Toaster se réabonne
// et recevrait immédiatement l'état courant).
function drainToasts(): void {
  let ids: number[] = [];
  const unsub = subscribeToasts((items) => {
    ids = items.map((i) => i.id);
  });
  unsub();
  for (const id of ids) dismissToast(id);
}

afterEach(() => {
  cleanup();
  drainToasts();
});

describe("Card", () => {
  it("rend le titre et le contenu, fusionne la className", () => {
    render(
      <Card title="Équipe" className="mt-4">
        <p>Contenu</p>
      </Card>,
    );
    expect(screen.getByRole("heading", { name: "Équipe" })).toBeTruthy();
    expect(screen.getByText("Contenu")).toBeTruthy();
  });

  it("sans titre : aucun en-tête, la classe de base reste appliquée", () => {
    const { container } = render(
      <Card>
        <p>X</p>
      </Card>,
    );
    expect(container.querySelector(".irm-card__title")).toBeNull();
    expect(container.querySelector(".irm-card")).not.toBeNull();
  });
});

describe("Toaster (liaison store <-> React)", () => {
  it("affiche un toast émis, avec sa variante et la région a11y", () => {
    render(<Toaster />);
    act(() => {
      toast("Équipe sauvegardée", { variant: "success", durationMs: 0 });
    });

    const region = screen.getByRole("status");
    expect(region.getAttribute("aria-live")).toBe("polite");
    expect(screen.getByText("Équipe sauvegardée")).toBeTruthy();
    expect(region.querySelector(".irm-toast--success")).not.toBeNull();
  });

  it("empile plusieurs toasts et les ferme individuellement", () => {
    render(<Toaster />);
    act(() => {
      toast("A", { variant: "info", durationMs: 0 });
      toast("B", { variant: "error", durationMs: 0 });
    });
    expect(screen.getByText("A")).toBeTruthy();
    expect(screen.getByText("B")).toBeTruthy();

    const closes = screen.getAllByRole("button", {
      name: "Fermer la notification",
    });
    expect(closes).toHaveLength(2);

    fireEvent.click(closes[0] as HTMLElement);
    expect(screen.queryByText("A")).toBeNull();
    expect(screen.getByText("B")).toBeTruthy();
  });
});
