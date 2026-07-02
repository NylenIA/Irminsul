"use client";

import { useState, useTransition, type CSSProperties } from "react";
import { Button, Card, ErrorState, Input } from "@irminsul/ui";
import {
  AMPLIFYING_BASE,
  ENGINE_CONTRACT_VERSION,
  TRANSFORMATIVE_BASE,
  type DirectHitPreview as PreviewData,
  type PlayerCharacterBuild,
} from "@irminsul/engine-client";
import type { CharacterSummary } from "@/lib/roster";
import { previewDirectHitAction } from "./engine-actions";
import { loadPlayerBuildAction } from "./build-actions";

type UiState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; preview: PreviewData }
  | { kind: "insufficient_data"; fields: string[] }
  | { kind: "validation_error"; issues: string[] }
  | { kind: "engine_error"; issues: string[] }
  | { kind: "stale_contract"; got: string };

type BuildState =
  | { kind: "none" }
  | { kind: "loading" }
  | { kind: "found"; build: PlayerCharacterBuild }
  | { kind: "not_in_scan" }
  | { kind: "no_scan" };

const FIELD_LABELS: Record<string, string> = {
  character: "Personnage",
  scalingPct: "Multiplicateur de talent (%)",
  scalingStat: "Stat porteuse (ATQ/PV/DÉF finale)",
};

const REACTION_LABELS: Record<string, string> = {
  "forward-vaporize": "Vaporisation (Pyro→Hydro, ×2)",
  "reverse-vaporize": "Vaporisation inverse (Hydro→Pyro, ×1.5)",
  "forward-melt": "Fonte (Cryo→Pyro, ×2)",
  "reverse-melt": "Fonte inverse (Pyro→Cryo, ×1.5)",
  swirl: "Dispersion",
  superconduct: "Supraconduction",
  "electro-charged": "Électrocution",
  overloaded: "Surcharge",
  shattered: "Brisure",
  burning: "Combustion",
  bloom: "Bourgeonnement",
  hyperbloom: "Exubérance",
  burgeon: "Burgeon",
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
  const [reaction, setReaction] = useState("");
  const [elementalMastery, setElementalMastery] = useState("");
  const [state, setState] = useState<UiState>({ kind: "idle" });
  const [buildState, setBuildState] = useState<BuildState>({ kind: "none" });
  const [pending, startTransition] = useTransition();

  function onCharacterChange(name: string): void {
    setCharacter(name);
    if (!name) {
      setBuildState({ kind: "none" });
      return;
    }
    setBuildState({ kind: "loading" });
    startTransition(async () => {
      const res = await loadPlayerBuildAction(name);
      if (res.ok) setBuildState({ kind: "found", build: res.build });
      else setBuildState({ kind: res.reason === "no_scan" ? "no_scan" : "not_in_scan" });
    });
  }

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
        reaction: reaction || null,
        elementalMastery: num(elementalMastery),
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
        Calcul déterministe d&apos;<strong>un coup isolé</strong> (réaction optionnelle) — ce
        n&apos;est ni un DPS de rotation, ni une valeur garantie en jeu. Champs vides = valeurs
        par défaut du moteur (affichées avec le résultat).
      </p>

      <div style={grid}>
        <label style={fieldStyle}>
          <span style={labelStyle}>Personnage *</span>
          <select
            value={character}
            onChange={(e) => onCharacterChange(e.target.value)}
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
        <label style={fieldStyle}>
          <span style={labelStyle}>Réaction</span>
          <select value={reaction} onChange={(e) => setReaction(e.target.value)} className="irm-input" aria-label="Réaction élémentaire">
            <option value="">— aucune —</option>
            <optgroup label="Amplifiantes (multiplient le coup)">
              {Object.keys(AMPLIFYING_BASE).map((k) => (
                <option key={k} value={k}>{REACTION_LABELS[k] ?? k}</option>
              ))}
            </optgroup>
            <optgroup label="Transformatives (dégâts propres, sans crit)">
              {Object.keys(TRANSFORMATIVE_BASE).map((k) => (
                <option key={k} value={k}>{REACTION_LABELS[k] ?? k}</option>
              ))}
            </optgroup>
          </select>
        </label>
        {reaction ? (
          <label style={fieldStyle}>
            <span style={labelStyle}>Maîtrise élémentaire</span>
            <Input inputMode="numeric" value={elementalMastery} onChange={(e) => setElementalMastery(e.target.value)} placeholder="défaut 0" aria-label="Maîtrise élémentaire" />
          </label>
        ) : null}
      </div>

      <BuildPanel state={buildState} />

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
            <span style={srOnly}>Calcul en cours…</span>
          </div>
        ) : state.kind === "insufficient_data" ? (
          <div className="irm-state" role="status">
            <span className="irm-state__title">Données insuffisantes</span>
            <span>
              Champs requis : {state.fields.map((f) => FIELD_LABELS[f] ?? f).join(", ")}.
              Renseigne-les pour lancer l&apos;aperçu — rien n&apos;est inventé à ta place.
            </span>
          </div>
        ) : state.kind === "validation_error" ? (
          <ErrorState title="Paramètres invalides">{state.issues.join(" ")}</ErrorState>
        ) : state.kind === "engine_error" ? (
          <ErrorState title="Erreur du moteur">{state.issues.join(" ")}</ErrorState>
        ) : state.kind === "stale_contract" ? (
          <ErrorState title="Contrat de calcul obsolète">
            Version reçue {state.got}, attendue {ENGINE_CONTRACT_VERSION}. Recharge la page.
          </ErrorState>
        ) : state.kind === "success" ? (
          <ResultCard preview={state.preview} />
        ) : null}
      </div>
    </Card>
  );
}

function BuildPanel({ state }: { state: BuildState }): React.ReactElement | null {
  if (state.kind === "none") return null;
  if (state.kind === "loading") {
    return <span className="irm-skeleton" style={{ width: "50%", display: "block", marginTop: 10 }} />;
  }
  if (state.kind === "no_scan") return null; // pas de scan local : la saisie manuelle reste la voie normale
  if (state.kind === "not_in_scan") {
    return (
      <p style={{ color: "var(--irm-text-faint)", fontSize: 12.5, marginTop: 10 }} role="status">
        Personnage absent du scan du compte — saisie manuelle.
      </p>
    );
  }
  const b = state.build;
  return (
    <section className="irm-card irm-fade-in" style={{ marginTop: 10, padding: 12 }} aria-label="Build du compte">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span className="irm-badge irm-badge--verified">build du compte</span>
        <span className="irm-badge">source {b.scannerName ?? "scan"}</span>
        {b.importedAt ? <span className="irm-badge">importé le {b.importedAt}</span> : null}
        <span className="irm-badge irm-badge--gold">confiance {b.confidence === "high" ? "haute" : b.confidence}</span>
      </div>
      <p style={{ color: "var(--irm-text-dim)", fontSize: 13, margin: "8px 0 0" }}>
        Niv. {b.level ?? "?"} · C{b.constellation ?? "?"} · talents{" "}
        {b.talents ? `${b.talents.normal ?? "?"}/${b.talents.skill ?? "?"}/${b.talents.burst ?? "?"}` : "?"}
        {b.weapon ? ` · ${b.weapon.id}${b.weapon.refinement ? ` R${b.weapon.refinement}` : ""}` : ""}
        {b.artifactSlots ? ` · ${b.artifactSlots.length} artéfacts scannés` : ""}
      </p>
      <p style={{ color: "var(--irm-text-faint)", fontSize: 12, margin: "6px 0 0" }}>
        Manquant (jamais estimé) : {b.missing.join(" ; ")}
      </p>
    </section>
  );
}

function ResultCard({ preview }: { preview: PreviewData }): React.ReactElement {
  const r = preview.outcome.result;
  const p = preview.outcome.provenance;
  const reaction = preview.reaction;
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
        {reaction?.type === "amplifying" ? (
          <span className="irm-badge irm-badge--verified">
            {REACTION_LABELS[reaction.detail.reaction] ?? reaction.detail.reaction} ×{reaction.detail.amplifying_multiplier}
          </span>
        ) : null}
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

      {reaction?.type === "transformative" ? (
        <div className="irm-card" style={{ marginTop: 10, padding: 10 }} role="group" aria-label="Réaction transformative">
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <span className="irm-badge irm-badge--verified">
              {REACTION_LABELS[reaction.detail.reaction] ?? reaction.detail.reaction}
            </span>
            <span className="irm-figure">{fmt.format(reaction.detail.damage)}</span>
            <span style={{ color: "var(--irm-text-faint)", fontSize: 12 }}>
              dégâts de réaction (sans crit, niv. 90, EM {reaction.detail.em_bonus > 0 ? "comptée" : "0"})
            </span>
          </div>
        </div>
      ) : null}

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
          {reaction ? reaction.provenance.assumptions.map((a) => <li key={a}>{a}</li>) : null}
          <li>
            Formule : {p.formula} · statut registre : {p.registryStatus} · mult. DEF{" "}
            {r.defenseMultiplier.toFixed(3)} · mult. RES {r.resistanceMultiplier.toFixed(3)}
            {reaction ? ` · réactions : ${reaction.provenance.source}` : ""}.
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
