import type { InputHTMLAttributes } from "react";

export type InputProps = InputHTMLAttributes<HTMLInputElement>;

export function Input({ className, ...rest }: InputProps): React.ReactElement {
  return <input className={className ? `irm-input ${className}` : "irm-input"} {...rest} />;
}
