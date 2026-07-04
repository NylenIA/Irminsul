import Link from "next/link";
import { ENGINE_CONTRACT_VERSION, REACTION_CONTRACT_VERSION } from "@irminsul/engine-client";
import { getTeamRepository } from "@irminsul/data-access";
import { loadAccountSummary } from "@/server/account";

export const dynamic = "force-dynamic";

/** Tableau de bord honnête : uniquement des comptes et états RÉELS (aucun chiffre décoratif). */
export default async function DashboardPage(): Promise<React.ReactElement> {
  const account = await loadAccountSummary();
  let teamsCount: number | null = null;
  try {
    teamsCount = (await getTeamRepository().list()).length;
  } catch {
    teamsCount = null; // base locale non initialisée
  }

  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 1100, margin: "0 auto", display: "grid", gap: 18 }}>
      <header>
        <h1 style={{ margin: 0 }}>Irminsul — Archive astrale</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Observatoire tactique local-first : tes données restent sur ta machine.
        </p>
      </header>

      <section style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        <Link href="/characters" style={{ textDecoration: "none", color: "inherit" }}>
          <article className="irm-card irm-fade-in">
            <h2 className="irm-card__title">Personnages</h2>
            {account ? (
              <>
                <p className="irm-figure">{account.characters.length}</p>
                <p style={{ color: "var(--irm-text-faint)", fontSize: 12, margin: "4px 0 0" }}>
                  scannés · {account.scannerName ?? "scan local"} · {account.importedAt ?? "date inconnue"}
                </p>
              </>
            ) : (
              <p style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>Aucun scan importé.</p>
            )}
          </article>
        </Link>

        <Link href="/team-lab" style={{ textDecoration: "none", color: "inherit" }}>
          <article className="irm-card irm-fade-in">
            <h2 className="irm-card__title">Laboratoire d&apos;équipes</h2>
            {teamsCount !== null ? (
              <>
                <p className="irm-figure">{teamsCount}</p>
                <p style={{ color: "var(--irm-text-faint)", fontSize: 12, margin: "4px 0 0" }}>
                  équipes sauvegardées en local (SQLite)
                </p>
              </>
            ) : (
              <p style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>
                Base locale non initialisée (<code>prisma migrate dev</code>).
              </p>
            )}
          </article>
        </Link>

        <article className="irm-card irm-fade-in">
          <h2 className="irm-card__title">Moteur de calcul</h2>
          <p style={{ color: "var(--irm-text-dim)", fontSize: 13, margin: 0 }}>
            <span className="irm-badge irm-badge--verified" style={{ marginRight: 6 }}>contrat {ENGINE_CONTRACT_VERSION}</span>
            <span className="irm-badge irm-badge--verified">{REACTION_CONTRACT_VERSION}</span>
          </p>
          <p style={{ color: "var(--irm-text-faint)", fontSize: 12, margin: "6px 0 0" }}>
            Formules vérifiées (parité Python prouvée par goldens). Coup isolé + 13 réactions.
          </p>
        </article>
      </section>
    </main>
  );
}
