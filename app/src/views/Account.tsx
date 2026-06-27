/** Écran Compte — branché sur le moteur réel (irminsul.account via IPC Tauri).
 * Aucune donnée factice : états vide / chargement / erreur / prêt, avec provenance
 * et fraîcheur issues du scan importé. */
import { useEffect, useState } from "react";
import {
  getProfile,
  importGood,
  isDesktop,
  type AccountProfile,
  type ImportSummary,
} from "../engine";

type State =
  | { kind: "loading" }
  | { kind: "no-desktop" }
  | { kind: "empty" }
  | { kind: "ready"; profile: AccountProfile }
  | { kind: "error"; message: string };

function freshness(snapshot: string | null): string {
  if (!snapshot) return "inconnue";
  const d = new Date(`${snapshot}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return snapshot;
  const days = Math.floor((Date.now() - d.getTime()) / 86_400_000);
  return `${snapshot} — il y a ${days} j`;
}

export function Account(): JSX.Element {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [path, setPath] = useState("");
  const [importing, setImporting] = useState(false);
  const [lastImport, setLastImport] = useState<ImportSummary | null>(null);

  async function refresh(): Promise<void> {
    if (!isDesktop()) {
      setState({ kind: "no-desktop" });
      return;
    }
    setState({ kind: "loading" });
    try {
      const res = await getProfile();
      setState(res.status === "ok" ? { kind: "ready", profile: res.profile } : { kind: "empty" });
    } catch (e) {
      setState({ kind: "error", message: String(e) });
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function onImport(): Promise<void> {
    const p = path.trim();
    if (!p) return;
    setImporting(true);
    try {
      const res = await importGood(p);
      if ("error" in res) {
        setState({ kind: "error", message: res.error });
      } else {
        setLastImport(res.import);
        await refresh();
      }
    } catch (e) {
      setState({ kind: "error", message: String(e) });
    } finally {
      setImporting(false);
    }
  }

  const importForm = (
    <form
      className="import"
      onSubmit={(ev) => {
        ev.preventDefault();
        void onImport();
      }}
    >
      <label htmlFor="good-path">Chemin du fichier GOOD (export Inventory Kamera)</label>
      <div className="import__row">
        <input
          id="good-path"
          type="text"
          value={path}
          placeholder="C:\\...\\genshinData_GOOD_....json"
          onChange={(ev) => setPath(ev.target.value)}
        />
        <button type="submit" disabled={importing || !path.trim()}>
          {importing ? "Import…" : "Importer"}
        </button>
      </div>
    </form>
  );

  if (state.kind === "loading") return <p>Chargement du compte…</p>;

  if (state.kind === "no-desktop") {
    return (
      <p className="empty-state">
        Les fonctions de compte (import GOOD, provenance) s'exécutent dans l'application
        desktop Irminsul. Ouvert ici en mode navigateur : le moteur local n'est pas disponible.
      </p>
    );
  }

  if (state.kind === "error") {
    return (
      <div>
        <p className="error" role="alert">Erreur moteur : {state.message}</p>
        <button type="button" onClick={() => void refresh()}>Réessayer</button>
      </div>
    );
  }

  if (state.kind === "empty") {
    return (
      <div>
        <p className="empty-state">Aucun compte importé. Importe ton export GOOD pour commencer.</p>
        {importForm}
      </div>
    );
  }

  const { profile } = state;
  const c = profile.counts;
  return (
    <div className="account">
      <section className="provenance">
        <h2>Provenance &amp; fraîcheur</h2>
        <dl>
          <dt>Snapshot</dt><dd>{freshness(profile.snapshot_date)}</dd>
          <dt>Source</dt><dd>{profile.source ?? "—"} (GOOD v{profile.good_version ?? "?"})</dd>
          <dt>SHA-256</dt><dd>{profile.sha256 ? `${profile.sha256.slice(0, 12)}…` : "—"}</dd>
        </dl>
      </section>

      <section className="counts">
        <h2>Inventaire scanné</h2>
        <ul>
          <li>{c.characters} personnages</li>
          <li>{c.weapons} armes</li>
          <li>{c.artifacts} artéfacts</li>
          <li>{c.materials} catégories de matériaux</li>
          {typeof c.unresolved_characters === "number" && (
            <li>{c.unresolved_characters} personnage(s) non résolu(s)</li>
          )}
        </ul>
      </section>

      {profile.unresolved.length > 0 && (
        <p className="warn">
          Non résolus (exclus des recos) : {profile.unresolved.join(", ")}.
        </p>
      )}

      {lastImport && (
        <section className="import-report">
          <h2>Dernier import</h2>
          <p>
            snapshot {lastImport.snapshot}
            {lastImport.idempotent_skip ? " (déjà importé — idempotent)" : ""} ·
            {" "}anomalies : {lastImport.validation.BLOCKING} bloquantes,
            {" "}{lastImport.validation.ERROR} erreurs, {lastImport.validation.WARNING} avertissements.
          </p>
        </section>
      )}

      <details>
        <summary>Réimporter un GOOD</summary>
        {importForm}
      </details>
    </div>
  );
}
