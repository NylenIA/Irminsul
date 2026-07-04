"use client";

import { useMemo, useState, useTransition, type CSSProperties } from "react";
import { Button, Card, ErrorState, Input } from "@irminsul/ui";
import type { RotationAction, RotationActionKind, RotationResult } from "@irminsul/engine-client";
import { calculateRotationAction } from "./rotation-actions";

export interface TeamOption {
  id: string;
  name: string;
  members: string[];
}

type UiState =
  | { kind: "idle" }
  | { kind: "calculating" }
  | { kind: "success"; result: RotationResult }
  | { kind: "partial"; result: RotationResult }
  | { kind: "validation_error"; issues: string[] }
  | { kind: "engine_error"; message: string };

const KINDS: RotationActionKind[] = [
  "normal_attack", "charged_attack", "plunging_attack", "skill", "burst", "swap", "wait",
];
const KIND_LABELS: Record<RotationActionKind, string> = {
  normal_attack: "Attaque normale", charged_attack: "Attaque chargée",
  plunging_attack: "Attaque plongeante", skill: "Compétence", burst: "Déchaînement",
  swap: "Changement", wait: "Attente",
};

const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
let counter = 0;
const nextId = (): string => `act-${++counter}`;

function defaultAction(actor: string, start: number): RotationAction {
  return {
    id: nextId(), actorId: actor, kind: "normal_attack", startTime: start, duration: 1,
    talentSlot: "combat1", talentLabel: "1-Hit DMG", talentLevel: 10,
  };
}

export function RotationsClient({ teams }: { teams: TeamOption[] }): React.ReactElement {
  const [teamId, setTeamId] = useState(teams[0]?.id ?? "");
  const team = useMemo(() => teams.find((t) => t.id === teamId), [teams, teamId]);
  const [actions, setActions] = useState<RotationAction[]>([]);
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [pending, startTransition] = useTransition();

  const members = team?.members ?? [];

  function addAction(): void {
    const start = actions.reduce((max, a) => Math.max(max, a.startTime + a.duration), 0);
    setActions((prev) => [...prev, defaultAction(members[0] ?? "", start)]);
  }
  function update(id: string, patch: Partial<RotationAction>): void {
    setActions((prev) => prev.map((a) => (a.id === id ? { ...a, ...patch } : a)));
  }
  function remove(id: string): void {
    setActions((prev) => prev.filter((a) => a.id !== id));
  }

  function calculate(): void {
    setState({ kind: "calculating" });
    startTransition(async () => {
      const res = await calculateRotationAction(members, actions);
      if (res.ok) {
        setState({ kind: res.result.complete ? "success" : "partial", result: res.result });
      } else if (res.kind === "validation_error") {
        setState({ kind: "validation_error", issues: res.issues });
      } else {
        setState({ kind: "engine_error", message: res.message });
      }
    });
  }

  if (teams.length === 0) {
    return (
      <div className="irm-state" role="status">
        <span className="irm-state__title">Aucune équipe sauvegardée</span>
        <span>Crée une équipe dans le Laboratoire d&apos;équipes, puis reviens ici.</span>
      </div>
    );
  }

  return (
    <>
      <Card title="Équipe & actions">
        <label style={{ display: "grid", gap: 4, maxWidth: 320 }}>
          <span style={{ color: "var(--irm-text-dim)", fontSize: 13 }}>Équipe</span>
          <select
            value={teamId}
            onChange={(e) => { setTeamId(e.target.value); setActions([]); setState({ kind: "idle" }); }}
            className="irm-input"
            aria-label="Équipe sauvegardée"
          >
            {teams.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </label>
        <p style={{ color: "var(--irm-text-faint)", fontSize: 12, margin: "8px 0 0" }}>
          Membres : {members.join(", ") || "—"}
        </p>

        <div style={{ marginTop: 12, display: "grid", gap: 8 }}>
          {actions.map((a, i) => (
            <ActionRow key={a.id} action={a} index={i} members={members} onUpdate={update} onRemove={remove} />
          ))}
        </div>

        <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
          <Button onClick={addAction} disabled={members.length === 0}>+ Action</Button>
          <Button variant="primary" onClick={calculate} disabled={pending || actions.length === 0}>
            {pending ? "Calcul…" : "Calculer la rotation"}
          </Button>
        </div>
      </Card>

      <div style={{ marginTop: 14 }}>
        {state.kind === "calculating" ? (
          <div role="status" aria-live="polite" style={{ display: "grid", gap: 8 }}>
            <span className="irm-skeleton" style={{ width: "40%", minHeight: 26 }} />
            <span className="irm-skeleton" style={{ width: "65%" }} />
          </div>
        ) : state.kind === "validation_error" ? (
          <ErrorState title="Rotation invalide">{state.issues.join(" ")}</ErrorState>
        ) : state.kind === "engine_error" ? (
          <ErrorState title="Erreur du moteur">{state.message}</ErrorState>
        ) : state.kind === "success" || state.kind === "partial" ? (
          <ResultView result={state.result} />
        ) : null}
      </div>
    </>
  );
}

function ActionRow({
  action, index, members, onUpdate, onRemove,
}: {
  action: RotationAction; index: number; members: string[];
  onUpdate: (id: string, patch: Partial<RotationAction>) => void;
  onRemove: (id: string) => void;
}): React.ReactElement {
  const isDamage = !["swap", "wait"].includes(action.kind);
  return (
    <div className="irm-card" style={{ padding: 10, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "end" }}>
      <span style={{ color: "var(--irm-text-faint)", fontSize: 12, minWidth: 20 }}>{index + 1}</span>
      <Field label="Perso">
        <select value={action.actorId} onChange={(e) => onUpdate(action.id, { actorId: e.target.value })} className="irm-input" aria-label={`Personnage action ${index + 1}`}>
          {members.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </Field>
      <Field label="Type">
        <select value={action.kind} onChange={(e) => onUpdate(action.id, { kind: e.target.value as RotationActionKind })} className="irm-input" aria-label={`Type action ${index + 1}`}>
          {KINDS.map((k) => <option key={k} value={k}>{KIND_LABELS[k]}</option>)}
        </select>
      </Field>
      <Field label="Début (s)"><Input style={{ width: 70 }} inputMode="decimal" value={String(action.startTime)} onChange={(e) => onUpdate(action.id, { startTime: Number(e.target.value) })} aria-label={`Début action ${index + 1}`} /></Field>
      <Field label="Durée (s)"><Input style={{ width: 70 }} inputMode="decimal" value={String(action.duration)} onChange={(e) => onUpdate(action.id, { duration: Number(e.target.value) })} aria-label={`Durée action ${index + 1}`} /></Field>
      {isDamage ? (
        <>
          <Field label="Talent (slot)"><Input style={{ width: 90 }} value={action.talentSlot ?? ""} onChange={(e) => onUpdate(action.id, { talentSlot: e.target.value })} aria-label={`Talent slot action ${index + 1}`} /></Field>
          <Field label="Label"><Input style={{ width: 110 }} value={action.talentLabel ?? ""} onChange={(e) => onUpdate(action.id, { talentLabel: e.target.value })} aria-label={`Talent label action ${index + 1}`} /></Field>
          <Field label="Niv"><Input style={{ width: 50 }} inputMode="numeric" value={String(action.talentLevel ?? "")} onChange={(e) => onUpdate(action.id, { talentLevel: Number(e.target.value) })} aria-label={`Talent niveau action ${index + 1}`} /></Field>
        </>
      ) : null}
      <Button variant="ghost" onClick={() => onRemove(action.id)} aria-label={`Supprimer action ${index + 1}`}>✕</Button>
    </div>
  );
}

function ResultView({ result: r }: { result: RotationResult }): React.ReactElement {
  const conf = r.confidence === "high" ? "haute" : r.confidence === "medium" ? "moyenne" : "faible";
  return (
    <section className="irm-card irm-halo irm-fade-in" aria-label="Résultat de la rotation">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span className={`irm-badge ${r.complete ? "irm-badge--verified" : "irm-badge--warn"}`}>
          {r.complete ? "rotation complète" : "rotation incomplète"}
        </span>
        <span className={`irm-badge ${r.complete ? "irm-badge--gold" : "irm-badge--warn"}`}>confiance {conf}</span>
        <span className="irm-badge">contrat {r.contractVersion}</span>
        <span className="irm-badge">durée {r.duration}s</span>
      </div>

      <div style={figures}>
        <div>
          <div style={figLabel}>DPS moyen</div>
          <div className="irm-figure irm-figure--hero">
            {r.averageDamagePerSecond !== null ? fmt.format(r.averageDamagePerSecond) : "—"}
          </div>
          {r.averageDamagePerSecond === null ? (
            <div style={{ color: "var(--irm-danger)", fontSize: 11 }}>non calculé (rotation incomplète)</div>
          ) : null}
        </div>
        <div>
          <div style={figLabel}>Dégâts totaux</div>
          <div className="irm-figure">{r.totalDamage !== null ? fmt.format(r.totalDamage) : "—"}</div>
        </div>
      </div>

      <table className="irm-table" style={{ marginTop: 12 }} aria-label="Dégâts par action">
        <thead><tr><th scope="col" style={th}>#</th><th scope="col" style={th}>Perso</th><th scope="col" style={th}>Action</th><th scope="col" style={th}>Dégâts</th></tr></thead>
        <tbody>
          {r.actions.map((a, i) => (
            <tr key={i}>
              <td style={{ color: "var(--irm-text-faint)" }}>{i + 1}</td>
              <td>{a.actorId}</td>
              <td>{KIND_LABELS[a.kind] ?? a.kind}</td>
              <td style={{ fontFamily: "var(--irm-mono)" }}>
                {a.damage !== null ? fmt.format(a.damage) : (
                  <span className="irm-badge irm-badge--warn" style={{ fontSize: 10 }}>incomplet</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {r.warnings.length > 0 ? (
        <div style={{ marginTop: 10 }} role="status">
          <span className="irm-badge irm-badge--warn" style={{ marginRight: 6 }}>avertissements</span>
          <ul style={{ margin: "6px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
            {r.warnings.map((w) => <li key={w}>{w}</li>)}
          </ul>
        </div>
      ) : null}

      <details style={{ marginTop: 10 }}>
        <summary style={{ cursor: "pointer", color: "var(--irm-cyan)", fontSize: 13 }}>Hypothèses & provenance</summary>
        <ul style={{ margin: "8px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {r.assumptions.map((a) => <li key={a}>{a}</li>)}
          <li>Moteur : {String(r.provenance["engine"] ?? "python")} · données talents : {String(r.provenance["talent_data"] ?? "n/a")}.</li>
        </ul>
      </details>
    </section>
  );
}

const Field = ({ label, children }: { label: string; children: React.ReactNode }): React.ReactElement => (
  <label style={{ display: "grid", gap: 3 }}>
    <span style={{ color: "var(--irm-text-faint)", fontSize: 11 }}>{label}</span>
    {children}
  </label>
);
const figures: CSSProperties = { display: "flex", gap: 32, flexWrap: "wrap", marginTop: 12 };
const figLabel: CSSProperties = { color: "var(--irm-text-faint)", fontSize: 12 };
const th: CSSProperties = { textAlign: "left", color: "var(--irm-text-dim)", fontSize: 12, fontWeight: 500, padding: "2px 8px 2px 0" };
