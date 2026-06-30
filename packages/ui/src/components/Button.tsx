import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "default" | "primary" | "ghost" | "danger";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  children: ReactNode;
}

const CLASS: Record<Variant, string> = {
  default: "irm-btn",
  primary: "irm-btn irm-btn--primary",
  ghost: "irm-btn irm-btn--ghost",
  danger: "irm-btn irm-btn--danger",
};

export function Button({
  variant = "default",
  className,
  type = "button",
  children,
  ...rest
}: ButtonProps): React.ReactElement {
  const cls = className ? `${CLASS[variant]} ${className}` : CLASS[variant];
  return (
    <button type={type} className={cls} {...rest}>
      {children}
    </button>
  );
}
