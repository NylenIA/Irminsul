/** Écran Compte — branché sur le moteur réel (irminsul.account via IPC Tauri).
 * Aucune donnée factice : états vide / chargement / erreur / prêt, provenance,
 * fraîcheur, import par sélecteur natif, et fiches personnages / armes / artéfacts. */
import { useEffect, useState } from "react";
import {
  getProfile,
  getRoster,
  importGood,
  isDesktop,
  pickGoodFile,
  type AccountProfile,
  type ImportSummary,
  type Roster,
} from "../engine";

type State =
  | { kind: "loading" }
  | { kind: "no-desktop" }
  | { kind: "empty" }
  | { kind: "ready"; profile: AccountProfile }
  | { kind: "error"; message: string };

type Tab = "chars" | "weapons" | "arts";

function freshness(snapshot: string | null): string {
  if (!snapshot) return "inconnue";
  const d = new Date(`${snapshot}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return snapshot;
  const days = Math.floor((Date.now() - d.getTime()) / 86_400_000);
  return `${snapshot} — il y a ${days} j`;
}

export function Account(): JSX.Element {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [roster, setRoster] = useState<Roster | null>(null);
  const [tab, setTab] = useState<Tab>("chars");
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
      if (res.status !== "ok") {
        setRoster(null);
        setState({ kind: "empty" });
        return;
      }
      setState({ kind: "ready", profile: res.profile });
      const r = await getRoster();
      setRoster(r.status === "ok" ? r.roster : null);
    } catch (e) {
      setState({ kind: "error", message: String(e) });
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function chooseAndImport(): Promise<void> {
    setImporting(true);
    try {
      const p = await pickGoodFile();
      if (!p) return;
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

  const importButton = (
    <button type="button" onClick={() => void chooseAndImport()} disabled={importing}>
      {importing ? "Import…" : "Choisir un fichier GOOD…"}
    </button>
  );

  if (state.kind === "loading") return <p>Chargement du compte…</p>;
  if (state.kind === "no-desktop") {
    return (
      <p className="empty-state">
        Les fonctions de compte s'exécutent dans l'application desktop Irminsul.
        Ouvert en mode navigateur : le moteur local n'est pas disponible.
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
        <p className="empty-state">Aucun compte importé. Importe ton export GOOD (Inventory Kamera) pour commencer.</p>
        {importButton}
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
        <p>
          {c.characters} personnages · {c.weapons} armes · {c.artifacts} artéfacts ·{" "}
          {c.materials} matériaux. {importButton}
        </p>
        {lastImport && (
          <p className="import-report">
            Dernier import : snapshot {lastImport.snapshot}
            {lastImport.idempotent_skip ? " (idempotent)" : ""} — {lastImport.validation.BLOCKING}{" "}
            bloquantes, {lastImport.validation.ERROR} erreurs, {lastImport.validation.WARNING} avert.
          </p>
        )}
        {profile.unresolved.length > 0 && (
          <p className="warn">Non résolus (exclus des recos) : {profile.unresolved.join(", ")}.</p>
        )}
      </section>

      <nav className="tabs" aria-label="Fiches">
        {(["chars", "weapons", "arts"] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={"tab" + (t === tab ? " is-active" : "")}
            aria-current={t === tab ? "true" : undefined}
            onClick={() => setTab(t)}
          >
            {t === "chars" ? "Personnages" : t === "weapons" ? "Armes" : "Artéfacts"}
          </button>
        ))}
      </nav>

      {!roster ? (
        <p className="empty-state">Inventaire indisponible.</p>
      ) : tab === "chars" ? (
        <div className="scroll">
          <table className="table">
            <thead>
              <tr><th>Personnage</th><th>Niv</th><th>C</th><th>Talents</th><th>Arme</th><th>Arté.</th><th>Set</th></tr>
            </thead>
            <tbody>
              {roster.characters.map((ch) => (
                <tr key={ch.key}>
                  <td>{ch.key}</td>
                  <td>{ch.level ?? "?"}</td>
                  <td>C{ch.constellation ?? "?"}</td>
                  <td>{ch.talents.auto ?? "?"}/{ch.talents.skill ?? "?"}/{ch.talents.burst ?? "?"}</td>
                  <td>{ch.weapon ? `${ch.weapon.key} lv${ch.weapon.level ?? "?"} R${ch.weapon.refinement ?? "?"}` : "—"}</td>
                  <td>{ch.artifacts}/5</td>
                  <td>{ch.dominant_set ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : tab === "weapons" ? (
        <div className="scroll">
          <table className="table">
            <thead><tr><th>Arme</th><th>Niv</th><th>Raff.</th><th>Équipée par</th></tr></thead>
            <tbody>
              {roster.weapons.map((w, i) => (
                <tr key={`${w.key}-${i}`}>
                  <td>{w.key}</td>
                  <td>{w.level ?? "?"}</td>
                  <td>R{w.refinement ?? "?"}</td>
                  <td>{w.location ?? "libre"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="scroll">
          <table className="table">
            <thead><tr><th>Set d'artéfacts</th><th>Total</th><th>Équipés</th><th>Libres</th></tr></thead>
            <tbody>
              {roster.artifact_sets.map((s) => (
                <tr key={s.setKey}>
                  <td>{s.setKey}</td>
                  <td>{s.total}</td>
                  <td>{s.equipped}</td>
                  <td>{s.total - s.equipped}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
