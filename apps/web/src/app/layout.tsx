import type { Metadata } from "next";
import { Toaster } from "@irminsul/ui";
import { IrminsulLogo } from "@/components/IrminsulLogo";
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
          <a href="/" className="irm-brand" aria-label="Irminsul — accueil">
            <IrminsulLogo size={26} />
            <span className="irm-brand__name">Irminsul</span>
          </a>
          {/* Essentiel : le parcours de base d'un joueur. */}
          <a href="/" className="irm-btn irm-btn--ghost">Accueil</a>
          <a href="/characters" className="irm-btn irm-btn--ghost">Personnages</a>
          <a href="/team-lab" className="irm-btn irm-btn--ghost">Mes équipes</a>
          <span aria-hidden="true" style={{ alignSelf: "center", color: "var(--irm-border)", padding: "0 2px" }}>·</span>
          {/* Analyse : pour creuser (résultats toujours expliqués). */}
          <a href="/rotations" className="irm-btn irm-btn--ghost" title="Chiffrer une suite d'actions avec tes vrais builds">Dégâts d&apos;équipe</a>
          <a href="/team-compare" className="irm-btn irm-btn--ghost" title="Deux équipes, une cible commune, un verdict sourcé">Comparateur</a>
          <a href="/recommendations" className="irm-btn irm-btn--ghost" title="Améliorations classées, basées sur tes données">Recommandations</a>
          <a href="/simulation" className="irm-btn irm-btn--ghost" title="Simulations complètes gcsim (avancé)">Simulation</a>
          <span aria-hidden="true" style={{ alignSelf: "center", color: "var(--irm-border)", padding: "0 2px" }}>·</span>
          {/* Système. */}
          <a href="/import-export" className="irm-btn irm-btn--ghost" title="Sauvegarder / restaurer tes équipes">Import/Export</a>
          <a href="/diagnostic" className="irm-btn irm-btn--ghost" title="État de l'app, du moteur et de la base">Diagnostic</a>
        </nav>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
