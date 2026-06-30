import type { HTMLAttributes, ReactNode } from "react";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  children: ReactNode;
}

export function Card({ title, className, children, ...rest }: CardProps): React.ReactElement {
  const cls = className ? `irm-card ${className}` : "irm-card";
  return (
    <div className={cls} {...rest}>
      {title ? <h3 className="irm-card__title">{title}</h3> : null}
      {children}
    </div>
  );
}
