import type { ReactNode } from "react";

/** État vide — invite à agir (pas de remplissage décoratif). */
export function EmptyState({ title, children }: { title: string; children?: ReactNode }): React.ReactElement {
  return (
    <div className="irm-state" role="status">
      <span className="irm-state__title">{title}</span>
      {children ? <span>{children}</span> : null}
    </div>
  );
}

/** État de chargement — annonce l'attente sans bloquer le clavier. */
export function LoadingState({ label = "Chargement…" }: { label?: string }): React.ReactElement {
  return (
    <div className="irm-state" role="status" aria-live="polite">
      <span className="irm-spinner" aria-hidden="true" />
      <span className="irm-state__title">{label}</span>
    </div>
  );
}

/** État d'erreur — explique quoi et comment réparer, dans la voix de l'interface. */
export function ErrorState({ title, children }: { title: string; children?: ReactNode }): React.ReactElement {
  return (
    <div className="irm-state irm-state--error" role="alert">
      <span className="irm-state__title">{title}</span>
      {children ? <span>{children}</span> : null}
    </div>
  );
}
