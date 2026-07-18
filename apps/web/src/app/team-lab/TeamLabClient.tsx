"use client";

import { useMemo, useState, useTransition, type CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, ConfirmDialog, EmptyState, ErrorState, Input, Select } from "@irminsul/ui";
import type { SavedTeamDTO } from "@irminsul/data-access";
import { type CharacterSummary, ROSTER_SOURCE_LABEL } from "@/lib/roster";
import {
  saveTeamAction,
  deleteTeamAction,
  renameTeamAction,
  duplicateTeamAction,
} from "./actions";
import { DirectHitPreview } from "./DirectHitPreview";

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
  roster: CharacterSummary[];
  loadError: boolean;
}): React.ReactElement {
  const router = useRouter();
  const [slots, setSlots] = useState<SlotState[]>(EMPTY_SLOTS);
  const [name, setName] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return q ? roster.filter((c) => c.name.toLowerCase().includes(q)) : roster;
  }, [roster, search]);

  function updateSlot(index: number, patch: Partial<SlotState>): void {
    setSlots((prev) => prev.map((s, i) => (i === index ? { ...s, ...patch } : s)));
  }
  function takenElsewhere(index: number): Set<string> {
    return new Set(slots.filter((_, i) => i !== index).map((s) => s.character).filter(Boolean));
  }
  function run(action: () => Promise<{ ok: true } | { ok: false; error: string }>): void {
    setError(null);
    startTransition(async () => {
      const res = await action();
      if (res.ok) router.refresh();
      else setError(res.error);
    });
  }

  function onSave(): void {
    const members = slots
      .map((s, slot) => ({ character: s.character.trim(), role: s.role.trim() || null, slot }))
      .filter((m) => m.character.length > 0);
    const carry = members[0]?.character ?? null;
    run(async () => {
      const res = await saveTeamAction({ name: name.trim(), carry, members });
      if (res.ok) {
        setSlots(EMPTY_SLOTS);
        setName("");
      }
      return res;
    });
  }
  function onRenameSubmit(id: string): void {
    run(async () => {
      const res = await renameTeamAction(id, editName);
      if (res.ok) setEditingId(null);
      return res;
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
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ex. Sandrone Lunar-Crystallize" />
          </label>
          <label style={{ display: "grid", gap: 4 }}>
            <span style={labelStyle}>Rechercher un personnage</span>
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Filtrer la liste…" aria-label="Rechercher un personnage" />
          </label>

          <div style={slotsGrid}>
            {slots.map((s, i) => {
              const taken = takenElsewhere(i);
              const options = filtered.filter((c) => !taken.has(c.name) || c.name === s.character);
              return (
                <fieldset key={i} style={fieldsetStyle}>
                  <legend style={{ color: "var(--irm-cyan)", fontSize: 12 }}>Emplacement {i + 1}</legend>
                  <Select value={s.character} onChange={(e) => updateSlot(i, { character: e.target.value })} aria-label={`Personnage, emplacement ${i + 1}`}>
                    <option value="">— vide —</option>
                    {options.map((c) => (
                      <option key={c.id} value={c.name}>{c.element ? `${c.name} · ${c.element}` : c.name}</option>
                    ))}
                  </Select>
                  <Input value={s.role} onChange={(e) => updateSlot(i, { role: e.target.value })} placeholder="Rôle (optionnel)" style={{ marginTop: 6 }} aria-label={`Rôle, emplacement ${i + 1}`} />
                </fieldset>
              );
            })}
          </div>

          {error ? <ErrorState title="Action impossible">{error}</ErrorState> : null}

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <Button variant="primary" onClick={onSave} disabled={pending}>
              {pending ? "Enregistrement…" : "Sauvegarder l'équipe"}
            </Button>
            <span style={{ color: "var(--irm-text-faint)", fontSize: 12 }}>
              Roster : {roster.length} personnages · source : {ROSTER_SOURCE_LABEL}
            </span>
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
          <EmptyState title="Aucune équipe pour l'instant">Compose et sauvegarde ta première équipe ci-dessus.</EmptyState>
        ) : (
          initialTeams.map((t) => (
            <Card key={t.id} title={editingId === t.id ? undefined : t.name}>
              {editingId === t.id ? (
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 8 }}>
                  <Input value={editName} onChange={(e) => setEditName(e.target.value)} aria-label={`Nouveau nom pour ${t.name}`} style={{ maxWidth: 280 }} autoFocus />
                  <Button variant="primary" onClick={() => onRenameSubmit(t.id)} disabled={pending}>Valider</Button>
                  <Button variant="ghost" onClick={() => setEditingId(null)} disabled={pending}>Annuler</Button>
                </div>
              ) : null}
              <div style={teamRow}>
                <span style={{ color: "var(--irm-text-dim)" }}>
                  {t.members.map((m) => m.character + (m.role ? ` (${m.role})` : "")).join(" · ") || "—"}
                </span>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  <Button variant="ghost" aria-label={`Renommer ${t.name}`} onClick={() => { setEditingId(t.id); setEditName(t.name); }} disabled={pending}>Renommer</Button>
                  <Button variant="ghost" aria-label={`Dupliquer ${t.name}`} onClick={() => run(() => duplicateTeamAction(t.id))} disabled={pending}>Dupliquer</Button>
                  <Button variant="danger" aria-label={`Supprimer ${t.name}`} onClick={() => setConfirmId(t.id)} disabled={pending}>Supprimer</Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </section>

      <DirectHitPreview roster={roster} />

      <ConfirmDialog
        open={confirmId !== null}
        title="Supprimer cette équipe ?"
        message="Cette action est définitive et ne peut pas être annulée."
        confirmLabel="Supprimer"
        cancelLabel="Annuler"
        onCancel={() => setConfirmId(null)}
        onConfirm={() => {
          const id = confirmId;
          setConfirmId(null);
          if (id) run(() => deleteTeamAction(id));
        }}
      />
    </main>
  );
}

const pageStyle: CSSProperties = { padding: "clamp(16px, 4vw, 40px)", maxWidth: 960, margin: "0 auto", display: "grid", gap: 20 };
const labelStyle: CSSProperties = { color: "var(--irm-text-dim)", fontSize: 13 };
const slotsGrid: CSSProperties = { display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))" };
const fieldsetStyle: CSSProperties = { border: "1px solid var(--irm-border)", borderRadius: 10, padding: 10, margin: 0 };
const teamRow: CSSProperties = { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" };
