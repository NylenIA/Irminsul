import Link from "next/link";
import { loadAccountSummary } from "@/server/account";
import type { PlayerCharacterBuild } from "@irminsul/engine-client";
import { ImportGoodForm } from "./ImportGoodForm";

export const dynamic = "force-dynamic";

export default async function CharactersPage(): Promise<React.ReactElement> {
  const account = await loadAccountSummary();

  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 1100, margin: "0 auto", display: "grid", gap: 18 }}>
      <header>
        <h1 style={{ margin: 0 }}>Personnages</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Roster réel importé de ton compte — aucune statistique estimée ni inventée.
        </p>
      </header>

      {account === null ? (
        <section className="irm-card" aria-label="Importer mon compte" style={{ maxWidth: 640 }}>
          <h2 className="irm-card__title" style={{ fontSize: 15 }}>
            Commence ici : importe ton compte
          </h2>
          <ImportGoodForm />
        </section>
      ) : (
        <>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }} aria-label="Provenance du scan">
            <span className="irm-badge irm-badge--verified">{account.characters.length} personnages scannés</span>
            <span className="irm-badge">source {account.scannerName ?? "scan local"}</span>
            {account.importedAt ? <span className="irm-badge">importé le {account.importedAt}</span> : null}
            <span className="irm-badge irm-badge--gold">
              confiance {account.format === "GOOD" ? "haute" : "moyenne"}
            </span>
          </div>

          <section
            style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))" }}
            aria-label="Liste des personnages"
          >
            {account.characters.map((c) => (
              <CharacterCard key={c.characterId} build={c} />
            ))}
          </section>

          <details style={{ fontSize: 13 }}>
            <summary style={{ cursor: "pointer", color: "var(--irm-text-dim)" }}>
              Mettre à jour le scan (nouveau fichier GOOD)
            </summary>
            <div style={{ marginTop: 8 }}>
              <ImportGoodForm compact />
            </div>
          </details>
        </>
      )}
    </main>
  );
}

function CharacterCard({ build }: { build: PlayerCharacterBuild }): React.ReactElement {
  return (
    <Link
      href={`/characters/${encodeURIComponent(build.characterId)}`}
      className="irm-card irm-fade-in"
      style={{ textDecoration: "none", color: "inherit", display: "block" }}
    >
      <h2 className="irm-card__title" style={{ fontSize: 15 }}>{build.characterId}</h2>
      <p style={{ margin: "4px 0 0", color: "var(--irm-text-dim)", fontSize: 13 }}>
        Niv. {build.level ?? "?"}
        {build.ascension !== undefined ? ` · A${build.ascension}` : ""}
        {build.constellation !== undefined ? ` · C${build.constellation}` : ""}
        {build.talents
          ? ` · ${build.talents.normal ?? "?"}/${build.talents.skill ?? "?"}/${build.talents.burst ?? "?"}`
          : ""}
      </p>
      {build.weapon ? (
        <p style={{ margin: "4px 0 0", color: "var(--irm-text-dim)", fontSize: 12.5 }}>
          {build.weapon.id}
          {build.weapon.refinement ? ` R${build.weapon.refinement}` : ""}
        </p>
      ) : null}
      {build.artifactSets && build.artifactSets.length > 0 ? (
        <p style={{ margin: "6px 0 0", fontSize: 12 }}>
          {build.artifactSets.map((s) => (
            <span key={s.set} className="irm-badge" style={{ marginRight: 4, marginBottom: 4 }}>
              {s.set} ×{s.count}
            </span>
          ))}
        </p>
      ) : null}
      <span style={{ display: "block", marginTop: 8, fontSize: 12, color: "var(--irm-cyan)" }}>
        Voir les stats finales →
      </span>
    </Link>
  );
}
