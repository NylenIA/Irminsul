import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  dismissToast,
  subscribeToasts,
  toast,
  type ToastItem,
} from "../src/components/Toast";

/** Le store est module-level : chaque test purge ce qu'il a créé. */
function drain(): void {
  let current: ToastItem[] = [];
  const unsub = subscribeToasts((items) => {
    current = items;
  });
  for (const item of current) dismissToast(item.id);
  unsub();
}

describe("store Toast (logique pure, sans DOM)", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    drain();
  });
  afterEach(() => {
    drain();
    vi.useRealTimers();
  });

  it("toast() ajoute un item (variante success par défaut) et notifie les abonnés", () => {
    let seen: ToastItem[] = [];
    const unsub = subscribeToasts((items) => {
      seen = items;
    });
    toast("Équipe sauvegardée");
    expect(seen).toHaveLength(1);
    expect(seen[0]!.message).toBe("Équipe sauvegardée");
    expect(seen[0]!.variant).toBe("success");
    unsub();
  });

  it("variante et durée personnalisées ; dismissToast retire l'item", () => {
    let seen: ToastItem[] = [];
    const unsub = subscribeToasts((items) => {
      seen = items;
    });
    toast("Échec", { variant: "error", durationMs: 0 }); // 0 = pas d'auto-dismiss
    expect(seen[0]!.variant).toBe("error");
    vi.advanceTimersByTime(60000);
    expect(seen).toHaveLength(1); // toujours là sans auto-dismiss
    dismissToast(seen[0]!.id);
    expect(seen).toHaveLength(0);
    unsub();
  });

  it("auto-dismiss après la durée par défaut (4 s)", () => {
    let seen: ToastItem[] = [];
    const unsub = subscribeToasts((items) => {
      seen = items;
    });
    toast("Temporaire");
    expect(seen).toHaveLength(1);
    vi.advanceTimersByTime(3999);
    expect(seen).toHaveLength(1);
    vi.advanceTimersByTime(1);
    expect(seen).toHaveLength(0);
    unsub();
  });

  it("l'abonnement reçoit l'état courant immédiatement ; unsubscribe stoppe les notifications", () => {
    toast("Déjà présent", { durationMs: 0 });
    let seen: ToastItem[] = [];
    let calls = 0;
    const unsub = subscribeToasts((items) => {
      seen = items;
      calls += 1;
    });
    expect(seen).toHaveLength(1); // état courant poussé à l'abonnement
    const callsBefore = calls;
    unsub();
    toast("Après unsubscribe", { durationMs: 0 });
    expect(calls).toBe(callsBefore); // plus notifié
  });

  it("plusieurs toasts s'empilent dans l'ordre d'émission", () => {
    let seen: ToastItem[] = [];
    const unsub = subscribeToasts((items) => {
      seen = items;
    });
    toast("un", { durationMs: 0 });
    toast("deux", { durationMs: 0 });
    toast("trois", { durationMs: 0 });
    expect(seen.map((t) => t.message)).toEqual(["un", "deux", "trois"]);
    unsub();
  });
});
