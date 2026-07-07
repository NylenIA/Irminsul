"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { Button, Card, ErrorState } from "@irminsul/ui";
import type { ImportPlan } from "@irminsul/engine-client";
import { applyImportAction, exportTeamsAction, previewImportAction } from "./io-actions";
import { isDesktop, pickImportNative, saveExport } from "@/lib/desktop-io";

const MAX_FILE_BYTES = 2 * 1024 * 1024;

type ImportState =
  | { kind: "idle" }
  | { kind: "previewing" }
  | { kind: "preview"; raw: string; plan: ImportPlan; meta: { appVersion: string; exportedAt: string; migrated: boolean } }
  | { kind: "applying" }
  | { kind: "applied"; created: number; updated: number }
  | { kind: "error"; message: string };

export function ImportExportClient(): React.ReactElement {
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [imp, setImp] = useState<ImportState>({ kind: "idle" });
  const [desktop, setDesktop] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const [pending, startTransition] = useTransition();
  useEffect(() => setDesktop(isDesktop()), []); // détection UNIQUE (adaptateur)

  function doExport(): void {
    startTransition(async () => {
      const res = await exportTeamsAction();
      // Adaptateur : dialogue NATIF Tauri en desktop, téléchargement Blob en web.
      try {
        const outcome = await saveExport(res.fileName, res.content);
        if (outcome.kind === "cancelled") setExportMsg("Export annulé.");
        else setExportMsg(`${res.teamCount} équipe(s) exportée(s) (irminsul-export/1.0) → ${outcome.kind === "saved" ? outcome.fileName : res.fileName}`);
      } catch (e) {
        setExportMsg(`Échec de l'export : ${String(e)}`);
      }
    });
  }

  function previewRaw(raw: string): void {
    setImp({ kind: "previewing" });
    startTransition(async () => {
      const res = await previewImportAction(raw);
      if (res.ok) {
        setImp({ kind: "preview", raw, plan: res.plan, meta: { appVersion: res.appVersion, exportedAt: res.exportedAt, migrated: res.migrated } });
      } else {
        setImp({ kind: "error", message: res.message });
      }
    });
  }

  function onFile(e: React.ChangeEvent<HTMLInputElement>): void {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_FILE_BYTES) {
      setImp({ kind: "error", message: "Fichier trop volumineux (> 2 Mo)." });
      return;
    }
    file.text().then(previewRaw);
  }

  function onNativeImport(): void {
    startTransition(async () => {
      try {
        const raw = await pickImportNative();
        if (raw === null) return; // annulation : sans effet
        previewRaw(raw);
      } catch (e) {
        setImp({ kind: "error", message: `Import natif impossible : ${String(e)}` });
      }
    });
  }

  function apply(raw: string): void {
    setImp({ kind: "applying" });
    startTransition(async () => {
      const res = await applyImportAction(raw);
      if (res.ok) setImp({ kind: "applied", created: res.created, updated: res.updated });
      else setImp({ kind: "error", message: res.message });
    });
  }

  function reset(): void {
    setImp({ kind: "idle" });
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <>
      <Card title="Exporter">
        <p style={{ color: "var(--irm-text-dim)", fontSize: 13, margin: "0 0 10px" }}>
          Exporte toutes tes équipes sauvegardées dans un fichier JSON versionné (avec checksum d&apos;intégrité).
        </p>
        <Button variant="primary" onClick={doExport} disabled={pending}>Exporter mes équipes</Button>
        {exportMsg ? <p style={{ color: "var(--irm-cyan)", fontSize: 13, marginTop: 8 }} role="status">{exportMsg}</p> : null}
      </Card>

      <Card title="Importer">
        <p style={{ color: "var(--irm-text-dim)", fontSize: 13, margin: "0 0 10px" }}>
          Sélectionne un fichier <code>irminsul-export</code>. Un aperçu s&apos;affiche <strong>avant</strong> toute écriture.
        </p>
        {desktop ? (
          <Button variant="primary" onClick={onNativeImport} disabled={pending} style={{ marginRight: 8 }}>
            Choisir un fichier (natif)…
          </Button>
        ) : null}
        <label className="irm-btn" style={{ cursor: "pointer", display: "inline-flex" }}>
          Choisir un fichier…
          <input ref={fileRef} type="file" accept="application/json,.json" onChange={onFile} aria-label="Fichier d'import" style={{ display: "none" }} />
        </label>

        <div style={{ marginTop: 12 }}>
          {imp.kind === "previewing" || imp.kind === "applying" ? (
            <span className="irm-skeleton" style={{ width: "55%", display: "block", minHeight: 22 }} />
          ) : imp.kind === "error" ? (
            <ErrorState title="Import impossible">{imp.message}</ErrorState>
          ) : imp.kind === "applied" ? (
            <div className="irm-state" role="status">
              <span className="irm-state__title">Import réussi</span>
              <span>{imp.created} créée(s), {imp.updated} remplacée(s).</span>
              <div style={{ marginTop: 8 }}><Button onClick={reset}>OK</Button></div>
            </div>
          ) : imp.kind === "preview" ? (
            <PreviewView plan={imp.plan} meta={imp.meta} onApply={() => apply(imp.raw)} onCancel={reset} pending={pending} />
          ) : null}
        </div>
      </Card>
    </>
  );
}

function PreviewView({
  plan, meta, onApply, onCancel, pending,
}: {
  plan: ImportPlan;
  meta: { appVersion: string; exportedAt: string; migrated: boolean };
  onApply: () => void; onCancel: () => void; pending: boolean;
}): React.ReactElement {
  return (
    <section className="irm-card irm-fade-in" aria-label="Aperçu de l'import">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 8 }}>
        <span className="irm-badge irm-badge--verified">{plan.created} à créer</span>
        <span className="irm-badge irm-badge--gold">{plan.updated} à remplacer</span>
        {plan.conflicts > 0 ? <span className="irm-badge irm-badge--warn">{plan.conflicts} ignorée(s)</span> : null}
        {meta.migrated ? <span className="irm-badge">migré</span> : null}
        <span className="irm-badge">exporté le {meta.exportedAt.slice(0, 10)} · app {meta.appVersion}</span>
      </div>
      <table className="irm-table" aria-label="Détail de l'aperçu">
        <thead><tr><th scope="col" style={{ textAlign: "left", fontSize: 12, color: "var(--irm-text-dim)" }}>Équipe</th><th scope="col" style={{ textAlign: "left", fontSize: 12, color: "var(--irm-text-dim)" }}>Action</th></tr></thead>
        <tbody>
          {plan.entries.map((e, i) => (
            <tr key={`${e.name}-${i}`}>
              <th scope="row" style={{ textAlign: "left", fontWeight: 500, color: "var(--irm-text-dim)" }}>{e.name}</th>
              <td style={{ fontSize: 12.5 }}>{e.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
        <Button variant="primary" onClick={onApply} disabled={pending || plan.total === plan.conflicts}>Appliquer l&apos;import</Button>
        <Button variant="ghost" onClick={onCancel}>Annuler</Button>
      </div>
    </section>
  );
}
