"use client";

import { useEffect, useRef } from "react";
import { Button } from "./Button";

export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

/** Dialog de confirmation accessible (native <dialog> : focus trap + Échap natifs). */
export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirmer",
  cancelLabel = "Annuler",
  onConfirm,
  onCancel,
}: ConfirmDialogProps): React.ReactElement {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) d.showModal();
    else if (!open && d.open) d.close();
  }, [open]);

  return (
    <dialog ref={ref} className="irm-dialog" onCancel={onCancel} onClose={onCancel} aria-label={title}>
      <h2 className="irm-dialog__title">{title}</h2>
      {message ? <p className="irm-dialog__msg">{message}</p> : null}
      <div className="irm-dialog__actions">
        <Button variant="ghost" onClick={onCancel}>
          {cancelLabel}
        </Button>
        <Button variant="danger" onClick={onConfirm}>
          {confirmLabel}
        </Button>
      </div>
    </dialog>
  );
}
