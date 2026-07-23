"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Button, toast } from "@irminsul/ui";
import { importGoodAction } from "./import-actions";

/**
 * Import du compte DANS l'app : choisir le fichier GOOD (.json) exporté par
 * InventoryKamera / Genshin Optimizer — aucun terminal, aucune commande.
 */
export function ImportGoodForm({ compact = false }: { compact?: boolean }): React.ReactElement {
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  function onSubmit(formData: FormData): void {
    setError(null);
    startTransition(async () => {
      const res = await importGoodAction(formData);
      if (res.ok) {
        toast(
          `Compte importé : ${res.characters} personnages, ${res.weapons} armes, ${res.artifacts} artéfacts.`,
          { variant: "success" },
        );
        router.refresh();
      } else {
        setError(res.error);
      }
    });
  }

  return (
    <form action={onSubmit} style={{ display: "grid", gap: 10 }} aria-label="Importer mon compte">
      {!compact ? (
        <p style={{ margin: 0, color: "var(--irm-text-dim)", fontSize: 13 }}>
          Scanne ton compte avec <strong>InventoryKamera</strong> (ou exporte depuis Genshin
          Optimizer), puis choisis le fichier <code>.json</code> obtenu — c&apos;est tout.
        </p>
      ) : null}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <input
          type="file"
          name="good"
          accept=".json,application/json"
          required
          aria-label="Fichier de scan GOOD (.json)"
          className="irm-input"
          style={{ maxWidth: 340 }}
        />
        <Button type="submit" variant="primary" disabled={pending}>
          {pending ? "Import en cours…" : compact ? "Mettre à jour le scan" : "Importer mon compte"}
        </Button>
      </div>
      {error ? (
        <p role="alert" style={{ margin: 0, color: "var(--irm-danger)", fontSize: 13 }}>
          {error}
        </p>
      ) : null}
    </form>
  );
}
