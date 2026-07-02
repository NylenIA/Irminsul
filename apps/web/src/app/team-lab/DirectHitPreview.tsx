"use client";

import { useState, useTransition, type CSSProperties } from "react";
import { Button, Card, ErrorState, Input } from "@irminsul/ui";
import {
  ENGINE_CONTRACT_VERSION,
  type DirectHitPreview as PreviewData,
} from "@irminsul/engine-client";
import type { CharacterSummary } from "@/lib/roster";
import { previewDirectHitAction } from "./engine-actions";

type UiState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; preview: PreviewData }
  | { kind: "insufficient_data"; fields: string[] }
  | { kind: "validation_error"; issues: string[] }
  | { kind: "engine_error"; issues: string[] }
  | { kind: "stale_contract"; got: string };

const FIELD_LABELS: Record<string, string> = {
  character: "Personnage",
  scalingPct: "Multiplicateur de talent (%)",
  scalingStat: "Stat porteuse (ATQ/PV/DÉF finale)",
};

const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });

function num(value: string): number | null {
  if (value.trim() === "") return null;
  const parsed = Number(value.replace(",", "."));
  return Number.isNaN(parsed) ? null : parsed;
}

export function DirectHitPreview({ roster }: { roster: CharacterSummary[] }): React.ReactElement {
  const [character, setCharacter] = useState("");
  const [scalingPct, setScalingPct] = useState("");
  const [scalingStat, setScalingStat] = useState("");
  const [critRatePct, setCritRatePct] = useState("");
  const [critDamagePct, setCritDamagePct] = useState("");
  const [damageBonusPct, setDamageBonusPct] = useState("");
  const [enemyLevel, setEnemyLevel] = useState("");
  const [enemyResistancePct, setEnemyResistancePct] = useState("");
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [pending, startTransition] = useTransition();

  function onPreview(): void {
    setState({ kind: "loading" });
    startTransition(async () => {
      const res = await previewDirectHitAction({
        character,
        scalingPct: num(scalingPct),
        scalingStat: num(scalingStat),
        critRatePct: num(critRatePct),
        critDamagePct: num(critDamagePct),
        damageBonusPct: num(damageBonusPct),
        enemyLevel: num(enemyLevel),
        enemyResistancePct: num(enemyResistancePct),
      });
      if (res.ok) {
        if (res.preview.contractVersion !== ENGINE_CONTRACT_VERSION) {
          setState({ kind: "stale_contract", got: res.preview.contractVersion });
        } else {
          setState({ kind: "success", preview: res.preview });
        }
      } else if (res.kind === "insufficient_data") {
        setState({ kind: "insufficient_data", fields: res.issues });
      } else if (res.kind === "validation_error") {
        setState({ kind: "validation_error", issues: res.issues });
      } else {
        setState({ kind: "engine_error", issues: res.issues });
      }
    });
  }

  return (
    <Card title="Aperçu de coup direct">
      <p style={{ color: "var(--irm-text-dim)", margin: "0 0 12px", fontSize: 13 }}>
        Calcul déterministe d&apos;<strong>un coup isolé</strong> — ce n&apos;est ni un DPS de
        rotation, ni une valeur garantie en jeu. Les champs vides utilisent les valeurs par
        défaut du moteur (affichées avec le résultat).
      </p>

      <div style={grid}>
        <label style={fieldStyle}>
          <span style={labelStyle}>Personnage *</span>
          <select
            value={character}
            onChange={(e) => setCharacter(e.target.value)}
            className="irm-input"
            aria-label="Personnage pour l'aperçu"
          >
            <option value="">— choisir —</option>
            {roster.map((c) => (
              <option key={c.id} value={c.name}>
                {c.element ? `${c.name} · ${c.element}` : c.name}
              </option>
            ))}
          </select>
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>Multiplicateur de talent (%) *</span>
          <Input inputMode="decimal" value={scalingPct} onChange={(e) => setScalingPct(e.target.value)} placeholder="ex. 250" />
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>Stat porteuse (ATQ finale…) *</span>
          <Input inputMode="decimal" value={scalingStat} onChange={(e) => setScalingStat(e.target.value)} placeholder="ex. 2000" />
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>Taux crit. (%)</span>
          <Input inputMode="decimal" value={critRatePct} onChange={(e) => setCritRatePct(e.target.value)} placeholder="défaut 5" />
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>Dégâts crit. (%)</span>
          <Input inputMode="decimal" value={critDamagePct} onChange={(e) => setCritDamagePct(e.target.value)} placeholder="défaut 50" />
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>Bonus de dégâts (%)</span>
          <Input inputMode="decimal" value={damageBonusPct} onChange={(e) => setDamageBonusPct(e.target.value)} placeholder="défaut 0" />
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>Niveau ennemi</span>
          <Input inputMode="numeric" value={enemyLevel} onChange={(e) => setEnemyLevel(e.target.value)} placeholder="défaut 100" />
        </label>
        <label style={fieldStyle}>
          <span style={labelStyle}>RES ennemie (%)</span>
          <Input inputMode="decimal" value={enemyResistancePct} onChange={(e) => setEnemyResistancePct(e.target.value)} placeholder="défaut 10" />
        </label>
      </div>

      <div style={{ marginTop: 12 }}>
        <Button variant="primary" onClick={onPreview} disabled={pending}>
          {pending ? "Calcul…" : "Calculer l'aperçu"}
        </Button>
      </div>

      <div style={{ marginTop: 14 }}>
        {state.kind === "loading" ? (
          <div role="status" aria-live="polite" style={{ display: "grid", gap: 8 }}>
            <span className="irm-skeleton" style={{ width: "38%", minHeight: 30 }} />
            <span className="irm-skeleton" style={{ width: "70%" }} />
            <span className="irm-skeleton" style={{ width: "55%" }} />
            <span style={srOnly}>Calcul en cours…</span>
          </div>
        ) : state.kind === "insufficient_data" ? (
          <div className="irm-state" role="status">
            <span className="irm-state__title">Données insuffisantes</span>
            <span>
              Champs requis :{" "}
              {state.fields.map((f) => FIELD_LABELS[f] ?? f).join(", ")}. Renseigne-les pour
              lancer l&apos;aperçu — rien n&apos;est inventé à ta place.
            </span>
          </div>
        ) : state.kind === "validation_error" ? (
          <ErrorState title="Paramètres invalides">{state.issues.join(" ")}</ErrorState>
        ) : state.kind === "engine_error" ? (
          <ErrorState title="Erreur du moteur">{state.issues.join(" ")}</ErrorState>
        ) : state.kind === "stale_contract" ? (
          <ErrorState title="Contrat de calcul obsolète">
            Version reçue {state.got}, attendue {ENGINE_CONTRACT_VERSION}. Recharge la page ;
            si l&apos;écart persiste, l&apos;app et le moteur doivent être mis à jour ensemble.
          </ErrorState>
        ) : state.kind === "success" ? (
          <ResultCard preview={state.preview} />
        ) : null}
      </div>
    </Card>
  );
}

function ResultCard({ preview }: { preview: PreviewData }): React.ReactElement {
  const r = preview.outcome.result;
  const p = preview.outcome.provenance;
  return (
    <section
      className="irm-card irm-halo irm-energy-line irm-fade-in"
      aria-label={`Résultat de l'aperçu pour ${preview.character}`}
    >
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <h3 className="irm-card__title" style={{ margin: 0 }}>
          {preview.character} — coup isolé
        </h3>
        <span className="irm-badge irm-badge--verified">formule vérifiée</span>
        <span className="irm-badge">moteur {p.engine}</span>
        <span className="irm-badge">contrat {preview.contractVersion}</span>
        <span className="irm-badge irm-badge--gold">confiance {preview.confidence.level}</span>
      </div>

      <div style={figures}>
        <div>
          <div style={figureLabel}>Attendu (moyenne crit.)</div>
          <div className="irm-figure irm-figure--hero">{fmt.format(r.expected)}</div>
        </div>
        <div>
          <div style={figureLabel}>Sans critique</div>
          <div className="irm-figure">{fmt.format(r.nonCrit)}</div>
        </div>
        <div>
          <div style={figureLabel}>Critique</div>
          <div className="irm-figure">{fmt.format(r.crit)}</div>
        </div>
      </div>

      {preview.defaultsUsed.length > 0 ? (
        <p style={{ color: "var(--irm-text-dim)", fontSize: 12.5, margin: "10px 0 0" }}>
          <span className="irm-badge irm-badge--warn" style={{ marginRight: 6 }}>défauts utilisés</span>
          {preview.defaultsUsed.join(", ")} — renseigne ces champs pour un aperçu fidèle à ton build.
        </p>
      ) : null}

      <details style={{ marginTop: 10 }}>
        <summary style={{ cursor: "pointer", color: "var(--irm-cyan)", fontSize: 13 }}>
          Hypothèses & provenance
        </summary>
        <ul style={{ margin: "8px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {p.assumptions.map((a) => (
            <li key={a}>{a}</li>
          ))}
          <li>
            Formule : {p.formula} · statut registre : {p.registryStatus} · multiplicateur DEF{" "}
            {r.defenseMultiplier.toFixed(3)} · multiplicateur RES {r.resistanceMultiplier.toFixed(3)}.
          </li>
        </ul>
      </details>
    </section>
  );
}

const grid: CSSProperties = { display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" };
const fieldStyle: CSSProperties = { display: "grid", gap: 4 };
const labelStyle: CSSProperties = { color: "var(--irm-text-dim)", fontSize: 13 };
const figures: CSSProperties = { display: "flex", gap: 28, flexWrap: "wrap", marginTop: 12 };
const figureLabel: CSSProperties = { color: "var(--irm-text-faint)", fontSize: 12 };
const srOnly: CSSProperties = { position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" };
