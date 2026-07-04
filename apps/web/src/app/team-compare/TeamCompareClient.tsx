"use client";

import { useState, useTransition } from "react";
import { Button, Card, ErrorState } from "@irminsul/ui";
import { compareTeamsAction } from "./compare-actions";
import type { TeamComparison } from "./compare-types";

export interface CompareTeamOption {
  id: string;
  name: string;
}

type UiState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; comparison: TeamComparison }
  | { kind: "error"; message: string };

export function TeamCompareClient({ teams }: { teams: CompareTeamOption[] }): React.ReactElement {
  const [aId, setAId] = useState(teams[0]?.id ?? "");
  const [bId, setBId] = useState(teams[1]?.id ?? "");
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [pending, startTransition] = useTransition();

  function compare(): void {
    setState({ kind: "loading" });
    startTransition(async () => {
      const res = await compareTeamsAction(aId, bId);
      setState(res.ok ? { kind: "success", comparison: res.comparison } : { kind: "error", message: res.message });
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
      <Card title="Choisir deux équipes">
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>Équipe A</span>
            <select value={aId} onChange={(e) => setAId(e.target.value)} className="irm-input" aria-label="Équipe A">
              {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>Équipe B</span>
            <select value={bId} onChange={(e) => setBId(e.target.value)} className="irm-input" aria-label="Équipe B">
              {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </label>
        </div>
        <div style={{ marginTop: 12 }}>
          <Button variant="primary" onClick={compare} disabled={pending}>
            {pending ? "Comparaison…" : "Comparer"}
          </Button>
        </div>
      </Card>

      <div style={{ marginTop: 14 }}>
        {state.kind === "loading" ? (
          <span className="irm-skeleton" style={{ width: "50%", display: "block", minHeight: 24 }} />
        ) : state.kind === "error" ? (
          <ErrorState title="Comparaison impossible">{state.message}</ErrorState>
        ) : state.kind === "success" ? (
          <ComparisonView c={state.comparison} />
        ) : null}
      </div>
    </>
  );
}

function ComparisonView({ c }: { c: TeamComparison }): React.ReactElement {
  return (
    <section className="irm-card irm-fade-in" aria-label="Résultat de la comparaison">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
        <span className="irm-badge">contrat {c.contractVersion}</span>
        <span className="irm-badge irm-badge--verified">{c.a.name}</span>
        <span className="irm-badge irm-badge--verified">{c.b.name}</span>
      </div>
      <table className="irm-table" aria-label="Dimensions comparées">
        <thead>
          <tr>
            <th scope="col" style={{ textAlign: "left", fontSize: 12, color: "var(--irm-text-dim)" }}>Dimension</th>
            <th scope="col" style={{ textAlign: "left", fontSize: 12, color: "var(--irm-text-dim)" }}>{c.a.name}</th>
            <th scope="col" style={{ textAlign: "left", fontSize: 12, color: "var(--irm-text-dim)" }}>{c.b.name}</th>
          </tr>
        </thead>
        <tbody>
          {c.dimensions.map((d) => (
            <tr key={d.label}>
              <th scope="row" style={{ textAlign: "left", fontWeight: 500, color: "var(--irm-text-dim)", padding: "4px 12px 4px 0" }}>
                {d.label}
                {!d.computable ? <span className="irm-badge irm-badge--warn" style={{ marginLeft: 6, fontSize: 10 }}>à venir</span> : null}
              </th>
              <td style={{ fontFamily: "var(--irm-mono)" }}>{d.a}</td>
              <td style={{ fontFamily: "var(--irm-mono)" }}>{d.b}</td>
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
