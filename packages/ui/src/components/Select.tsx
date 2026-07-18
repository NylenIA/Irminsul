import type { SelectHTMLAttributes } from "react";

export type SelectProps = SelectHTMLAttributes<HTMLSelectElement>;

/**
 * Select du design system — même surface que `Input` (.irm-input), apparence
 * native masquée, chevron dessiné aux tokens, focus visible. Toute l'a11y
 * (aria-label, id/htmlFor) passe par les props natives.
 */
export function Select({ className, ...rest }: SelectProps): React.ReactElement {
  return (
    <select
      className={className ? `irm-input irm-select ${className}` : "irm-input irm-select"}
      {...rest}
    />
  );
}
