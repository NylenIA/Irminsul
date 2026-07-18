"use client";

import { useState, useTransition, type CSSProperties } from "react";
import { Button, Card, ErrorState, Input, Select } from "@irminsul/ui";
import type {
  RotationAction,
  RotationActionKind,
  TeamComparisonResult,
  TeamPerformanceSummary,
} from "@irminsul/engine-client";
import { compareTeamsQuantitativeAction } from "./compare-actions";

export interface CompareTeamOption {
  id: string;
  name: string;
  members: string[];
}

type UiState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; comparison: TeamComparisonResult }
  | { kind: "validation_error"; issues: string[] }
  | { kind: "engine_error"; message: string };

const KIND_LABELS: Record<RotationActionKind, string> = {
  normal_attack: "Attaque normale", charged_attack: "Attaque chargée",
  plunging_attack: "Attaque plongeante", skill: "Compétence", burst: "Déchaînement",
  swap: "Changement", wait: "Attente",
};
const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const fmt1 = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });
let counter = 0;

function newAction(actor: string, start: number): RotationAction {
  return {
    id: `c-${++counter}`, actorId: actor, kind: "normal_attack", startTime: start, duration: 1,
    talentSlot: "combat1", talentLabel: "1-Hit DMG", talentLevel: 10,
  };
}

export function TeamCompareClient({ teams }: { teams: CompareTeamOption[] }): React.ReactElement {
  const [aId, setAId] = useState(teams[0]?.id ?? "");
  const [bId, setBId] = useState(teams[1]?.id ?? "");
  const [aActions, setAActions] = useState<RotationAction[]>([]);
  const [bActions, setBActions] = useState<RotationAction[]>([]);
  const [level, setLevel] = useState("100");
  const [res, setRes] = useState("10");
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [pending, startTransition] = useTransition();

  const teamA = teams.find((t) => t.id === aId);
  const teamB = teams.find((t) => t.id === bId);

  function compare(): void {
    setState({ kind: "loading" });
    startTransition(async () => {
      const target = { level: Number(level), resistance: Number(res) / 100, count: 1 };
      const r = await compareTeamsQuantitativeAction(
        { teamId: aId, actions: aActions },
        { teamId: bId, actions: bActions },
        target,
      );
      if (r.ok) setState({ kind: "success", comparison: r.comparison });
      else if (r.kind === "validation_error") setState({ kind: "validation_error", issues: r.issues });
      else setState({ kind: "engine_error", message: r.message });
    });
  }

  if (teams.length < 2) {
    return (
      <div className="irm-state" role="status">
        <span className="irm-state__title">Il faut au moins deux équipes</span>
        <span>Crée deux équipes dans le Laboratoire d&apos;équipes pour les comparer.</span>
      </div>
    );
  }

  return (
    <>
      <Card title="Cible commune">
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "end" }}>
          <label style={{ display: "grid", gap: 3 }}>
            <span style={lbl}>Niveau ennemi</span>
            <Input style={{ width: 90 }} inputMode="numeric" value={level} onChange={(e) => setLevel(e.target.value)} aria-label="Niveau ennemi" />
          </label>
          <label style={{ display: "grid", gap: 3 }}>
            <span style={lbl}>Résistance (%)</span>
            <Input style={{ width: 90 }} inputMode="decimal" value={res} onChange={(e) => setRes(e.target.value)} aria-label="Résistance ennemie" />
          </label>
          <span style={{ color: "var(--irm-text-faint)", fontSize: 12 }}>
            Les deux équipes sont comparées contre cette même cible.
          </span>
        </div>
      </Card>

      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", marginTop: 12 }}>
        <SideEditor label="Équipe A" teams={teams} teamId={aId} setTeamId={setAId} team={teamA} actions={aActions} setActions={setAActions} newAction={newAction} />
        <SideEditor label="Équipe B" teams={teams} teamId={bId} setTeamId={setBId} team={teamB} actions={bActions} setActions={setBActions} newAction={newAction} />
      </div>

      <div style={{ marginTop: 12 }}>
        <Button variant="primary" onClick={compare} disabled={pending || aActions.length === 0 || bActions.length === 0}>
          {pending ? "Comparaison…" : "Comparer quantitativement"}
        </Button>
      </div>

      <div style={{ marginTop: 14 }}>
        {state.kind === "loading" ? (
          <span className="irm-skeleton" style={{ width: "60%", display: "block", minHeight: 24 }} />
        ) : state.kind === "validation_error" ? (
          <ErrorState title="Comparaison invalide">{state.issues.join(" ")}</ErrorState>
        ) : state.kind === "engine_error" ? (
          <ErrorState title="Erreur du moteur">{state.message}</ErrorState>
        ) : state.kind === "success" ? (
          <ComparisonView c={state.comparison} />
        ) : null}
      </div>
    </>
  );
}

function SideEditor({
  label, teams, teamId, setTeamId, team, actions, setActions, newAction,
}: {
  label: string; teams: CompareTeamOption[]; teamId: string; setTeamId: (id: string) => void;
  team?: CompareTeamOption; actions: RotationAction[]; setActions: (a: RotationAction[]) => void;
  newAction: (actor: string, start: number) => RotationAction;
}): React.ReactElement {
  const members = team?.members ?? [];
  function add(): void {
    const start = actions.reduce((m, a) => Math.max(m, a.startTime + a.duration), 0);
    setActions([...actions, newAction(members[0] ?? "", start)]);
  }
  return (
    <Card title={label}>
      <Select value={teamId} onChange={(e) => { setTeamId(e.target.value); setActions([]); }} aria-label={`${label} équipe`} style={{ maxWidth: 260 }}>
        {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
      </Select>
      <p style={{ color: "var(--irm-text-faint)", fontSize: 12, margin: "6px 0" }}>{members.join(", ") || "—"}</p>
      <div style={{ display: "grid", gap: 6 }}>
        {actions.map((a, i) => (
          <div key={a.id} className="irm-card" style={{ padding: 8, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "end" }}>
            <span style={{ color: "var(--irm-text-faint)", fontSize: 11 }}>{i + 1}</span>
            <Select value={a.actorId} onChange={(e) => setActions(actions.map((x) => x.id === a.id ? { ...x, actorId: e.target.value } : x))} aria-label={`${label} perso ${i + 1}`}>
              {members.map((m) => <option key={m} value={m}>{m}</option>)}
            </Select>
            <Input style={{ width: 90 }} value={a.talentLabel ?? ""} onChange={(e) => setActions(actions.map((x) => x.id === a.id ? { ...x, talentLabel: e.target.value } : x))} aria-label={`${label} label ${i + 1}`} />
            <Input style={{ width: 46 }} inputMode="numeric" value={String(a.talentLevel ?? "")} onChange={(e) => setActions(actions.map((x) => x.id === a.id ? { ...x, talentLevel: Number(e.target.value) } : x))} aria-label={`${label} niveau ${i + 1}`} />
            <Button variant="ghost" onClick={() => setActions(actions.filter((x) => x.id !== a.id))} aria-label={`${label} supprimer ${i + 1}`}>✕</Button>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8 }}>
        <Button onClick={add} disabled={members.length === 0}>+ Action</Button>
      </div>
    </Card>
  );
}

function PerfCard({ s }: { s: TeamPerformanceSummary }): React.ReactElement {
  return (
    <div className="irm-card" style={{ padding: 12 }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <strong>{s.teamName}</strong>
        <span className={`irm-badge ${s.complete ? "irm-badge--verified" : "irm-badge--warn"}`}>
          {s.complete ? "complète" : "incomplète"}
        </span>
      </div>
      <div style={{ marginTop: 8 }}>
        <div style={figLabel}>DPS moyen</div>
        <div className="irm-figure irm-figure--hero">
          {s.averageDamagePerSecond !== null ? fmt.format(s.averageDamagePerSecond) : "—"}
        </div>
        <div style={figLabel}>Dégâts totaux : {s.totalDamage !== null ? fmt.format(s.totalDamage) : "—"} · durée {s.duration}s · {s.actionCount} actions</div>
      </div>
    </div>
  );
}

function ComparisonView({ c }: { c: TeamComparisonResult }): React.ReactElement {
  return (
    <section className="irm-card irm-halo irm-fade-in" aria-label="Résultat de la comparaison">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 8 }}>
        <span className="irm-badge">contrat {c.contractVersion}</span>
        <span className={`irm-badge ${c.complete ? "irm-badge--gold" : "irm-badge--warn"}`}>confiance {c.confidence === "high" ? "haute" : c.confidence === "medium" ? "moyenne" : "faible"}</span>
        <span className="irm-badge">cible niv {c.target.level} · RES {(c.target.resistance * 100).toFixed(0)}%</span>
      </div>

      <p style={{ fontSize: 15, fontWeight: 600, color: c.complete ? "var(--irm-cyan)" : "var(--irm-danger)", margin: "0 0 12px" }}>
        {c.verdict}
      </p>

      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
        <PerfCard s={c.left} />
        <PerfCard s={c.right} />
      </div>

      <table className="irm-table" style={{ marginTop: 12 }} aria-label="Écarts">
        <thead><tr><th scope="col" style={th}>Métrique</th><th scope="col" style={th}>{c.left.teamName}</th><th scope="col" style={th}>{c.right.teamName}</th><th scope="col" style={th}>Écart</th></tr></thead>
        <tbody>
          {c.differences.map((d) => (
            <tr key={d.metric}>
              <th scope="row" style={{ textAlign: "left", fontWeight: 500, color: "var(--irm-text-dim)" }}>{d.metric}</th>
              <td style={mono}>{d.left !== null ? fmt.format(d.left) : "—"}</td>
              <td style={mono}>{d.right !== null ? fmt.format(d.right) : "—"}</td>
              <td style={mono}>
                {d.computable && d.relativePct !== null ? (
                  <span style={{ color: d.winner === "tie" ? "var(--irm-text-dim)" : "var(--irm-cyan)" }}>
                    {d.absolute !== null && d.absolute >= 0 ? "+" : ""}{fmt1.format(d.relativePct)}%
                  </span>
                ) : <span className="irm-badge irm-badge--warn" style={{ fontSize: 10 }}>non comparable</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {c.warnings.length > 0 ? (
        <ul style={{ margin: "10px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {c.warnings.map((w) => <li key={w}>{w}</li>)}
        </ul>
      ) : null}

      <details style={{ marginTop: 10 }}>
        <summary style={{ cursor: "pointer", color: "var(--irm-cyan)", fontSize: 13 }}>Hypothèses</summary>
        <ul style={{ margin: "8px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {c.assumptions.map((a) => <li key={a}>{a}</li>)}
        </ul>
      </details>
    </section>
  );
}

const lbl: CSSProperties = { color: "var(--irm-text-faint)", fontSize: 11 };
const figLabel: CSSProperties = { color: "var(--irm-text-faint)", fontSize: 12 };
const th: CSSProperties = { textAlign: "left", color: "var(--irm-text-dim)", fontSize: 12, fontWeight: 500, padding: "2px 8px 2px 0" };
const mono: CSSProperties = { fontFamily: "var(--irm-mono)" };
