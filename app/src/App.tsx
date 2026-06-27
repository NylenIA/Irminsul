/**
 * Coquille applicative Irminsul — Phase 1 (fondation).
 * AUCUNE donnée Genshin factice : on n'affiche que des états réels (vide tant que
 * l'import compte / le backend ne sont pas branchés en Phase 2+).
 */
import { useState } from "react";
import { Account } from "./views/Account";

type View = "dashboard" | "account" | "teams" | "calc" | "gcsim" | "assistant";

const NAV: ReadonlyArray<{ id: View; label: string }> = [
  { id: "dashboard", label: "Tableau de bord" },
  { id: "account", label: "Compte" },
  { id: "teams", label: "Laboratoire d'équipes" },
  { id: "calc", label: "Calcul rapide" },
  { id: "gcsim", label: "Simulation gcsim" },
  { id: "assistant", label: "Assistant" },
];

export function App(): JSX.Element {
  const [view, setView] = useState<View>("dashboard");
  const current = NAV.find((n) => n.id === view);

  return (
    <div className="app">
      <a className="skip-link" href="#main">Aller au contenu</a>
      <header className="app__header">
        <span className="brand">Irminsul</span>
        <span className="brand__tag">arbre-mémoire</span>
      </header>
      <div className="app__body">
        <nav className="nav" aria-label="Navigation principale">
          {NAV.map((n) => (
            <button
              key={n.id}
              type="button"
              className={"nav__item" + (n.id === view ? " is-active" : "")}
              aria-current={n.id === view ? "page" : undefined}
              onClick={() => setView(n.id)}
            >
              {n.label}
            </button>
          ))}
        </nav>
        <main id="main" className="main" tabIndex={-1}>
          <h1>{current?.label ?? "Irminsul"}</h1>
          {view === "account" ? (
            <Account />
          ) : (
            <p className="empty-state">
              Écran en cours de construction. Les données réelles (calculs, gcsim, assistant)
              seront branchées aux phases suivantes — aucun contenu factice n'est affiché.
            </p>
          )}
        </main>
      </div>
    </div>
  );
}
