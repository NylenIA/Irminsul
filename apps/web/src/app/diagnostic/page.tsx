import { getDiagnosticAction } from "./diag-actions";
import { CopyReportButton } from "./CopyReportButton";

export const dynamic = "force-dynamic";

const fmt = new Intl.NumberFormat("fr-FR");

export default async function DiagnosticPage(): Promise<React.ReactElement> {
  const d = await getDiagnosticAction();
  const healthy =
    d.engine.ok && d.engine.frozen !== undefined && d.database.schema.status !== "drift";

  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 860, margin: "0 auto", display: "grid", gap: 14 }}>
      <header>
        <h1 style={{ margin: 0 }}>Diagnostic</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          État réel de l&apos;application, du moteur et de la base — rapport sanitizé (aucun secret, chemins masqués).
        </p>
      </header>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <span className={`irm-badge ${healthy ? "irm-badge--verified" : "irm-badge--warn"}`}>
          {healthy ? "sain" : d.engine.ok ? "avertissement" : "erreur moteur"}
        </span>
        <span className="irm-badge">{`mode ${d.app.mode}`}</span>
        <span className="irm-badge">{`Irminsul ${d.app.version}`}</span>
        <span className="irm-badge">{`Node ${d.app.nodeVersion}`}</span>
      </div>

      <section className="irm-card" aria-label="Moteur">
        <h2 className="irm-card__title" style={{ fontSize: 14 }}>Moteur</h2>
        {d.engine.ok ? (
          <table className="irm-table">
            <tbody>
              <Row k="Contrat IPC" v={d.engine.ipcContract} />
              <Row k="Gelé (frozen)" v={d.engine.frozen ? "oui (binaire empaqueté)" : "non (source Python)"} />
              <Row k="Commit" v={d.engine.gitCommit ?? "—"} />
              <Row k="SHA-256 binaire" v={d.engine.binarySha256 ? `${d.engine.binarySha256.slice(0, 16)}…` : "— (mode source)"} />
              <Row k="Python" v={d.engine.python} />
              <Row k="Méthodes" v={`${d.engine.methods.length} (${d.engine.methods.slice(0, 4).join(", ")}…)`} />
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--irm-danger)", fontSize: 13 }} role="alert">
            Moteur injoignable : {d.engine.error}. Vérifie que le sidecar est présent, puis relance l&apos;application.
          </p>
        )}
      </section>

      <section className="irm-card" aria-label="Base de données">
        <h2 className="irm-card__title" style={{ fontSize: 14 }}>Base de données</h2>
        <table className="irm-table">
          <tbody>
            <Row k="Emplacement" v={d.database.url} />
            <Row k="Taille" v={d.database.sizeBytes !== null ? `${fmt.format(d.database.sizeBytes)} octets` : "inaccessible"} />
            <Row k="Modifiée le" v={d.database.modifiedAt ?? "—"} />
            <Row k="Schéma" v={schemaLabel(d.database.schema.status)} />
          </tbody>
        </table>
        {d.database.schema.status === "drift" ? (
          <p role="alert" style={{ color: "var(--irm-danger)", fontSize: 13, marginTop: 8 }}>
            {d.database.schema.detail}
          </p>
        ) : null}
      </section>

      <section className="irm-card" aria-label="Sécurité et distribution">
        <h2 className="irm-card__title" style={{ fontSize: 14 }}>Sécurité & distribution</h2>
        <ul style={{ margin: 0, paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          <li>Serveur local en écoute sur 127.0.0.1 uniquement (jamais exposé au réseau).</li>
          <li>Bundle non signé — Windows SmartScreen affichera un avertissement à l&apos;installation.</li>
          {d.app.mode === "web" ? <li>Mode web : capacités desktop (moteur gelé, dialogues natifs) indisponibles.</li> : null}
        </ul>
      </section>

      <CopyReportButton report={d} />
    </main>
  );
}

function schemaLabel(status: "ok" | "drift" | "unknown"): string {
  if (status === "ok") return "à jour";
  if (status === "drift") return "en retard — ré-importe ton export";
  return "indéterminé";
}

function Row({ k, v }: { k: string; v: string }): React.ReactElement {
  return (
    <tr>
      <th scope="row" style={{ textAlign: "left", fontWeight: 500, color: "var(--irm-text-dim)", padding: "3px 12px 3px 0", width: 180 }}>{k}</th>
      <td style={{ fontFamily: "var(--irm-mono)", fontSize: 13 }}>{v}</td>
    </tr>
  );
}
