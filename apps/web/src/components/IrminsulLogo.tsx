/**
 * Marque Irminsul — constellation-arbre géométrique (brand guide : branches =
 * lignes de données, nœuds = étoiles, l'étoile de couronne = le nord/l'exactitude).
 * Dégradé cyan→violet (tokens). SVG inline pour permettre une animation CSS légère
 * (scintillement de la couronne), désactivée sous prefers-reduced-motion.
 */
export function IrminsulLogo({
  size = 28,
  animated = true,
  title = "Irminsul",
}: {
  size?: number;
  animated?: boolean;
  title?: string;
}): React.ReactElement {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      role="img"
      aria-label={title}
      className={animated ? "irm-logo irm-logo--animated" : "irm-logo"}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="irm-logo-grad" x1="4" y1="38" x2="36" y2="4" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#3bb8b2" />
          <stop offset="1" stopColor="#9b7fe6" />
        </linearGradient>
      </defs>
      <g stroke="url(#irm-logo-grad)" strokeWidth="1.6" strokeLinecap="round">
        <path d="M20 37 V7" />
        <path d="M20 29 L10 23" />
        <path d="M20 29 L30 23" />
        <path d="M20 22 L12 14" />
        <path d="M20 22 L28 14" />
      </g>
      <g fill="url(#irm-logo-grad)">
        <circle cx="10" cy="23" r="2" />
        <circle cx="30" cy="23" r="2" />
        <circle cx="12" cy="14" r="2" />
        <circle cx="28" cy="14" r="2" />
        <circle cx="20" cy="22" r="1.8" />
        <circle cx="20" cy="37" r="1.6" />
        <circle className="irm-logo__crown" cx="20" cy="6" r="3" />
      </g>
    </svg>
  );
}
