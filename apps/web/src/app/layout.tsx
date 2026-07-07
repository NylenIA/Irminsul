import type { Metadata } from "next";
import "@irminsul/ui/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Irminsul — Archive astrale",
  description: "Observatoire tactique Genshin — version web (en construction).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="fr">
      <body className="irm-root">
        <nav
          aria-label="Navigation principale"
          style={{
            display: "flex", gap: 4, padding: "10px clamp(16px, 4vw, 40px)",
            borderBottom: "1px solid var(--irm-border)", flexWrap: "wrap",
          }}
        >
          <a href="/" className="irm-btn irm-btn--ghost">Tableau de bord</a>
          <a href="/characters" className="irm-btn irm-btn--ghost">Personnages</a>
          <a href="/team-lab" className="irm-btn irm-btn--ghost">Laboratoire d&apos;équipes</a>
          <a href="/rotations" className="irm-btn irm-btn--ghost">Rotations</a>
          <a href="/team-compare" className="irm-btn irm-btn--ghost">Comparateur</a>
          <a href="/recommendations" className="irm-btn irm-btn--ghost">Recommandations</a>
          <a href="/import-export" className="irm-btn irm-btn--ghost">Import/Export</a>
          <a href="/diagnostic" className="irm-btn irm-btn--ghost">Diagnostic</a>
        </nav>
        {children}
      </body>
    </html>
  );
}
