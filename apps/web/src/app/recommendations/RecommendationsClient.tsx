"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { Button, Card, Select } from "@irminsul/ui";
import type {
  RecommendationItem,
  RecommendationObjective,
  RecommendationResult,
} from "@irminsul/engine-client";
import { getRecommendationsAction } from "./reco-actions";

export interface RecoTeamOption {
  id: string;
  name: string;
}

const OBJECTIVES: { value: RecommendationObjective; label: string }[] = [
  { value: "data_quality", label: "Qualité des données de mes builds" },
  { value: "highest_complete_dps", label: "Équipes prêtes pour un DPS fiable" },
  { value: "improve_current_team", label: "Améliorer une équipe précise" },
  { value: "balanced_team", label: "Équipe équilibrée (qualitatif)" },
  { value: "survivability", label: "Survie (qualitatif)" },
  { value: "reaction_focus", label: "Réactions (qualitatif)" },
];

const CONF_LABEL = { high: "haute", medium: "moyenne", low: "faible" } as const;

type UiState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; result: RecommendationResult };

export function RecommendationsClient({ teams }: { teams: RecoTeamOption[] }): React.ReactElement {
  const [objective, setObjective] = useState<RecommendationObjective>("data_quality");
  const [teamId, setTeamId] = useState(teams[0]?.id ?? "");
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [pending, startTransition] = useTransition();

  function analyze(): void {
    setState({ kind: "loading" });
    startTransition(async () => {
      const result = await getRecommendationsAction({
        objective,
        currentTeamId: objective === "improve_current_team" ? teamId : undefined,
      });
      setState({ kind: "success", result });
    });
  }

  return (
    <>
      <Card title="Objectif">
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "end" }}>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>Que veux-tu optimiser ?</span>
            <Select value={objective} onChange={(e) => setObjective(e.target.value as RecommendationObjective)} aria-label="Objectif">
              {OBJECTIVES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </Select>
          </label>
          {objective === "improve_current_team" ? (
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>Équipe</span>
              <Select value={teamId} onChange={(e) => setTeamId(e.target.value)} aria-label="Équipe à améliorer">
                {teams.length === 0 ? <option value="">Aucune équipe</option> : teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </Select>
            </label>
          ) : null}
          <Button variant="primary" onClick={analyze} disabled={pending}>
            {pending ? "Analyse…" : "Analyser"}
          </Button>
        </div>
      </Card>

      <div style={{ marginTop: 14 }}>
        {state.kind === "loading" ? (
          <div role="status" aria-live="polite" style={{ display: "grid", gap: 8 }}>
            <span className="irm-skeleton" style={{ width: "55%", minHeight: 22 }} />
            <span className="irm-skeleton" style={{ width: "70%" }} />
          </div>
        ) : state.kind === "success" ? (
          <ResultView result={state.result} />
        ) : null}
      </div>
    </>
  );
}

function ResultView({ result: r }: { result: RecommendationResult }): React.ReactElement {
  return (
    <section aria-label="Recommandations" style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span className="irm-badge">contrat {r.contractVersion}</span>
        <span className={`irm-badge ${r.confidence === "high" ? "irm-badge--verified" : "irm-badge--warn"}`}>confiance {CONF_LABEL[r.confidence]}</span>
        {r.provenance[0] ? <span className="irm-badge">source {r.provenance[0].source}{r.provenance[0].importedAt ? ` · ${r.provenance[0].importedAt}` : ""}</span> : null}
      </div>

      {r.recommendations.map((item, i) => <RecoCard key={i} item={item} />)}

      {r.missingData.length > 0 ? (
        <div className="irm-card" role="status" style={{ padding: 12 }}>
          <span className="irm-badge irm-badge--warn" style={{ marginRight: 6 }}>données manquantes</span>
          <ul style={{ margin: "6px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
            {r.missingData.map((m) => <li key={m}>{m}</li>)}
          </ul>
        </div>
      ) : null}

      <details className="irm-card">
        <summary style={{ cursor: "pointer", color: "var(--irm-cyan)", fontSize: 13 }}>Hypothèses & méthode</summary>
        <ul style={{ margin: "8px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {r.assumptions.map((a) => <li key={a}>{a}</li>)}
        </ul>
        <p style={{ color: "var(--irm-text-faint)", fontSize: 12, marginTop: 8 }}>
          Continuer : <Link href="/team-lab" className="irm-link">Team Lab</Link> · <Link href="/rotations" className="irm-link">Rotations</Link> · <Link href="/characters" className="irm-link">Personnages</Link>.
        </p>
      </details>
    </section>
  );
}

function RecoCard({ item }: { item: RecommendationItem }): React.ReactElement {
  return (
    <article className="irm-card irm-fade-in">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span className="irm-badge irm-badge--verified">{item.type}</span>
        <strong style={{ fontSize: 15 }}>{item.title}</strong>
        <span className={`irm-badge ${item.confidence === "high" ? "irm-badge--gold" : "irm-badge--warn"}`}>confiance {CONF_LABEL[item.confidence]}</span>
      </div>
      <p style={{ color: "var(--irm-text-dim)", fontSize: 13, margin: "6px 0" }}>{item.explanation}</p>
      {item.evidence.length > 0 ? (
        <div style={{ fontSize: 12.5 }}>
          <span style={{ color: "var(--irm-text-faint)" }}>Preuves : </span>
          {item.evidence.join(" · ")}
        </div>
      ) : null}
      {item.tradeoffs.length > 0 ? (
        <div style={{ fontSize: 12.5, marginTop: 4 }}>
          <span style={{ color: "var(--irm-text-faint)" }}>Compromis : </span>
          {item.tradeoffs.join(" · ")}
        </div>
      ) : null}
      <div style={{ fontSize: 12, color: "var(--irm-text-faint)", marginTop: 4 }}>
        Impact : {item.expectedImpact}
        {item.requiredData.length > 0 ? ` · données requises : ${item.requiredData.join(", ")}` : ""}
      </div>
    </article>
  );
}
