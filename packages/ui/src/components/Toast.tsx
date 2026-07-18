"use client";

import { useEffect, useState } from "react";

/**
 * Toasts du design system — feedback NON bloquant (succès/erreur/info).
 * Store module-level minimal (aucune dépendance, pas de provider à câbler) :
 * `toast("…")` depuis n'importe quel composant client ; `<Toaster/>` une seule
 * fois dans le layout. A11y : région `role="status"` + `aria-live="polite"`,
 * fermeture manuelle possible, animation coupée si `prefers-reduced-motion`.
 */
export interface ToastItem {
  id: number;
  message: string;
  variant: "success" | "error" | "info";
}

type Listener = (items: ToastItem[]) => void;

let items: ToastItem[] = [];
let nextId = 1;
const listeners = new Set<Listener>();

function emit(): void {
  for (const listener of listeners) listener([...items]);
}

export function dismissToast(id: number): void {
  items = items.filter((item) => item.id !== id);
  emit();
}

export function toast(
  message: string,
  options?: { variant?: ToastItem["variant"]; durationMs?: number },
): void {
  const item: ToastItem = { id: nextId++, message, variant: options?.variant ?? "success" };
  items = [...items, item];
  emit();
  const ttl = options?.durationMs ?? 4000;
  if (ttl > 0) setTimeout(() => dismissToast(item.id), ttl);
}

export function Toaster(): React.ReactElement {
  const [list, setList] = useState<ToastItem[]>([]);
  useEffect(() => {
    const listener: Listener = setList;
    listeners.add(listener);
    listener([...items]);
    return () => {
      listeners.delete(listener);
    };
  }, []);
  return (
    <div className="irm-toaster" role="status" aria-live="polite">
      {list.map((item) => (
        <div key={item.id} className={`irm-toast irm-toast--${item.variant}`}>
          <span>{item.message}</span>
          <button
            type="button"
            className="irm-toast__close"
            aria-label="Fermer la notification"
            onClick={() => dismissToast(item.id)}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
