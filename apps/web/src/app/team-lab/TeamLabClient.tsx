"use client";

import { useState, useTransition, type CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, EmptyState, ErrorState } from "@irminsul/ui";
import type { SavedTeamDTO } from "@irminsul/data-access";
import { saveTeamAction, deleteTeamAction } from "./actions";

interface SlotState {
  character: string;
  role: string;
}
const EMPTY_SLOTS: SlotState[] = [
  { character: "", role: "" },
  { character: "", role: "" },
  { character: "", role: "" },
  { character: "", role: "" },
];

export function TeamLabClient({
  initialTeams,
  roster,
  loadError,
}: {
  initialTeams: SavedTeamDTO[];
  roster: readonly string[];
  loadError: boolean;
}): React.ReactElement {
  const router = useRouter();
  const [slots, setSlots] = useState<SlotState[]>(EMPTY_SLOTS);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function updateSlot(index: number, patch: Partial<SlotState>): void {
    setSlots((prev) => prev.map((s, i) => (i === index ? { ...s, ...patch } : s)));
  }

  function onSave(): void {
    setError(null);
    const members = slots
      .map((s, slot) => ({ character: s.character.trim(), role: s.role.trim() || null, slot }))
      .filter((m) => m.character.length > 0);
    const carry = members[0]?.character ?? null;
    startTransition(async () => {
      const res = await saveTeamAction({ name: name.trim(), carry, members });
      if (res.ok) {
        setSlots(EMPTY_SLOTS);
        setName("");
        router.refresh();
      } else {
        setError(res.error);
      }
    });
  }

  function onDelete(id: string): void {
    setError(null);
    startTransition(async () => {
      const res = await deleteTeamAction(id);
      if (res.ok) router.refresh();
      else setError(res.error);
    });
  }

  return (
    <main style={pageStyle}>
      <header>
        <h1 style={{ margin: 0 }}>Laboratoire d&apos;équipes</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4 }}>
          Compose une équipe (jusqu&apos;à 4 emplacements), nomme-la et sauvegarde-la en local
          (SQLite, via Prisma). Aucune donnée DPS fictive.
        </p>
      </header>

      <Card title="Nouvelle équipe">
        <div style={{ display: "grid", gap: 12 }}>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={labelStyle}>Nom de l&apos;équipe</span>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex. Sandrone Lunar-Crystallize"
              style={inputStyle}
            />
          </label>

          <div style={slotsGrid}>
            {slots.map((s, i) => (
              <fieldset key={i} style={fieldsetStyle}>
                <legend style={{ color: "var(--irm-cyan)", fontSize: 12 }}>Emplacement {i + 1}</legend>
                <select
                  value={s.character}
                  onChange={(e) => updateSlot(i, { character: e.target.value })}
                  style={inputStyle}
                  aria-label={`Personnage, emplacement ${i + 1}`}
                >
                  <option value="">— vide —</option>
                  {roster.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <input
                  value={s.role}
                  onChange={(e) => updateSlot(i, { role: e.target.value })}
                  placeholder="Rôle (optionnel)"
                  style={{ ...inputStyle, marginTop: 6 }}
                  aria-label={`Rôle, emplacement ${i + 1}`}
                />
              </fieldset>
            ))}
          </div>

          {error ? <ErrorState title="Action impossible">{error}</ErrorState> : null}

          <div>
            <Button variant="primary" onClick={onSave} disabled={pending}>
              {pending ? "Enregistrement…" : "Sauvegarder l'équipe"}
            </Button>
          </div>
        </div>
      </Card>

      <section style={{ display: "grid", gap: 12 }}>
        <h2 style={{ margin: 0, fontSize: 16 }}>Équipes sauvegardées</h2>
        {loadError ? (
          <ErrorState title="Base locale indisponible">
            Initialise la base : <code>cd packages/data-access &amp;&amp; npx prisma migrate dev</code>.
          </ErrorState>
        ) : initialTeams.length === 0 ? (
          <EmptyState title="Aucune équipe pour l'instant">
            Compose et sauvegarde ta première équipe ci-dessus.
          </EmptyState>
        ) : (
          initialTeams.map((t) => (
            <Card key={t.id} title={t.name}>
              <div style={teamRow}>
                <span style={{ color: "var(--irm-text-dim)" }}>
                  {t.members.map((m) => m.character + (m.role ? ` (${m.role})` : "")).join(" · ") || "—"}
                </span>
                <Button variant="danger" onClick={() => onDelete(t.id)} disabled={pending}>
                  Supprimer
                </Button>
              </div>
            </Card>
          ))
        )}
      </section>
    </main>
  );
}

const pageStyle: CSSProperties = {
  padding: "clamp(16px, 4vw, 40px)",
  maxWidth: 960,
  margin: "0 auto",
  display: "grid",
  gap: 20,
};
const labelStyle: CSSProperties = { color: "var(--irm-text-dim)", fontSize: 13 };
const inputStyle: CSSProperties = {
  padding: "8px 10px",
  borderRadius: 6,
  background: "var(--irm-surface-2)",
  color: "var(--irm-text)",
  border: "1px solid var(--irm-border-strong)",
  font: "inherit",
  width: "100%",
};
const slotsGrid: CSSProperties = {
  display: "grid",
  gap: 10,
  gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
};
const fieldsetStyle: CSSProperties = {
  border: "1px solid var(--irm-border)",
  borderRadius: 10,
  padding: 10,
  margin: 0,
};
const teamRow: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 12,
  flexWrap: "wrap",
};
