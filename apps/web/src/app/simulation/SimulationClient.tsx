"use client";

import { useEffect, useState, useTransition, type CSSProperties } from "react";
import { Button, Card, ErrorState, Select, toast } from "@irminsul/ui";
import { teamToGcsimSkeleton } from "@irminsul/engine-client";
import { listTeamsForSimAction, runGcsimAction, type GcsimRunResult, type SimTeamOption } from "./actions";

type UiState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "done"; result: GcsimRunResult }
  | { kind: "error"; message: string };

const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const fmt1 = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });

const PLACEHOLDER = `// Colle ici une configuration gcsim complète, par exemple :
options iteration=50 duration=90 swap_delay=12;
target lvl=100 resist=0.1 pos=0,0;

bennett char lvl=90/90 cons=6 talent=9,9,9;
bennett add weapon="aquilafavonia" refine=1 lvl=90/90;
bennett add set="noblesseoblige" count=4;
bennett add stats hp=4780 atk=311 em=187 atk%=0.466 cr=0.311 cd=0.622;

active bennett;
bennett skill, attack;`;

export function SimulationClient(): React.ReactElement {
  const [config, setConfig] = useState("");
  const [teams, setTeams] = useState<SimTeamOption[]>([]);
  const [teamId, setTeamId] = useState("");
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    listTeamsForSimAction().then(setTeams).catch(() => setTeams([]));
  }, []);

  function onGenerateFromTeam(id: string): void {
    setTeamId(id);
    const team = teams.find((t) => t.id === id);
    if (!team) return;
    try {
      setConfig(teamToGcsimSkeleton(team.members));
      toast(`Squelette généré depuis « ${team.name} » — complète les TODO`);
    } catch (error) {
      toast(error instanceof Error ? error.message : "Génération impossible", { variant: "error" });
    }
  }

  function onRun(): void {
    setState({ kind: "running" });
    startTransition(async () => {
      const res = await runGcsimAction(config);
      if (res.ok) setState({ kind: "done", result: res.result });
      else setState({ kind: "error", message: res.message });
    });
  }

  return (
    <main style={pageStyle}>
      <header>
        <h1 style={{ margin: 0 }}>Simulation (gcsim)</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4 }}>
          Exécute une <strong>vraie simulation gcsim</strong> (binaire local) depuis une
          configuration au format gcsim. Le résultat dépend entièrement du script fourni
          (builds, rotation, cible) — ce n&apos;est pas une valeur garantie en jeu.
        </p>
      </header>

      <Card title="Configuration gcsim">
        <div style={{ display: "grid", gap: 10 }}>
          {teams.length > 0 ? (
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>
                Pré-remplir un squelette depuis une équipe sauvegardée
              </span>
              <Select
                value={teamId}
                onChange={(e) => onGenerateFromTeam(e.target.value)}
                aria-label="Équipe pour le squelette gcsim"
              >
                <option value="">— choisir une équipe —</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </Select>
            </label>
          ) : null}
          <textarea
            value={config}
            onChange={(e) => setConfig(e.target.value)}
            placeholder={PLACEHOLDER}
            aria-label="Configuration gcsim"
            className="irm-input"
            rows={14}
            style={{ fontFamily: "ui-monospace, monospace", fontSize: 12.5, resize: "vertical" }}
          />
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <Button variant="primary" onClick={onRun} disabled={pending}>
              {pending ? "Simulation en cours…" : "Lancer la simulation"}
            </Button>
            <span style={{ color: "var(--irm-text-faint)", fontSize: 12 }}>
              Peut prendre plusieurs secondes selon itérations/durée.
            </span>
          </div>
        </div>
      </Card>

      {state.kind === "error" ? (
        <ErrorState title="Simulation impossible">{state.message}</ErrorState>
      ) : null}

      {state.kind === "done" ? (
        <Card title="Résultat de simulation">
          {state.result.ok && state.result.parsed ? (
            <div role="group" aria-label="Résultat gcsim">
              <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "baseline" }}>
                <div>
                  <div style={figureLabel}>DPS moyen simulé</div>
                  <div className="irm-figure irm-figure--hero">{fmt.format(state.result.parsed.dps)}</div>
                </div>
                {state.result.parsed.damage !== undefined ? (
                  <div>
                    <div style={figureLabel}>Dégâts moyens</div>
                    <div className="irm-figure">{fmt.format(state.result.parsed.damage)}</div>
                  </div>
                ) : null}
                {state.result.parsed.duration !== undefined ? (
                  <div>
                    <div style={figureLabel}>Durée simulée</div>
                    <div className="irm-figure">{fmt1.format(state.result.parsed.duration)} s</div>
                  </div>
                ) : null}
              </div>
              {state.result.parsed.partial ? (
                <p style={noteStyle}>
                  <span className="irm-badge irm-badge--warn">parsing partiel</span> seul le DPS a
                  pu être extrait — vérifie la sortie brute.
                </p>
              ) : null}
              <p style={noteStyle}>
                <span className="irm-badge">SIMULATION</span> moyenne sur les itérations du script ;
                dépend du standard d&apos;investissement et de la rotation de TA config — à ne pas
                comparer à une autre sim sans mêmes hypothèses.
              </p>
            </div>
          ) : (
            <ErrorState title={`gcsim a échoué (code ${state.result.returncode})`}>
              Vérifie la syntaxe de la configuration — sortie brute ci-dessous.
            </ErrorState>
          )}
          <details style={{ marginTop: 10 }}>
            <summary style={{ cursor: "pointer", color: "var(--irm-cyan)", fontSize: 13 }}>
              Sortie brute gcsim
            </summary>
            <pre style={preStyle}>{state.result.output}</pre>
          </details>
        </Card>
      ) : null}
    </main>
  );
}

const pageStyle: CSSProperties = { padding: "clamp(16px, 4vw, 40px)", maxWidth: 960, margin: "0 auto", display: "grid", gap: 20 };
const figureLabel: CSSProperties = { color: "var(--irm-text-dim)", fontSize: 12 };
const noteStyle: CSSProperties = { color: "var(--irm-text-faint)", fontSize: 12.5, margin: "10px 0 0" };
const preStyle: CSSProperties = {
  whiteSpace: "pre-wrap", fontSize: 11.5, background: "var(--irm-surface-2)",
  padding: 10, borderRadius: 8, maxHeight: 320, overflow: "auto",
};
