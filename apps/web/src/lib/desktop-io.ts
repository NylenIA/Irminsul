"use client";

/**
 * Adaptateur Import/Export — UNE seule détection d'environnement, deux implémentations :
 * - desktop (Tauri) : dialogues natifs via commandes RESTREINTES (`save_export_file`,
 *   `pick_import_file`) — aucun chemin arbitraire ne transite depuis le frontend ;
 * - web : téléchargement Blob + <input type=file> (comportement historique inchangé).
 * Le contrat métier `irminsul-export/1.0` (validation/preview/apply) reste côté Server Actions.
 */

interface TauriGlobal {
  core: { invoke<T>(cmd: string, args?: Record<string, unknown>): Promise<T> };
}

function tauri(): TauriGlobal | null {
  const w = window as unknown as { __TAURI__?: TauriGlobal };
  return w.__TAURI__ ?? null;
}

export function isDesktop(): boolean {
  return tauri() !== null;
}

export type SaveOutcome =
  | { kind: "saved"; fileName: string }
  | { kind: "cancelled" }
  | { kind: "web_download" };

/** Export : dialogue natif en desktop (annulation propre), téléchargement Blob en web. */
export async function saveExport(fileName: string, content: string): Promise<SaveOutcome> {
  const t = tauri();
  if (t) {
    try {
      const saved = await t.core.invoke<string>("save_export_file", {
        defaultName: fileName,
        content,
      });
      return { kind: "saved", fileName: saved };
    } catch (e) {
      if (String(e).includes("annulé")) return { kind: "cancelled" };
      throw e;
    }
  }
  const blob = new Blob([content], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(url);
  return { kind: "web_download" };
}

/** Import desktop : dialogue natif → contenu (null = annulé). Web : géré par <input type=file>. */
export async function pickImportNative(): Promise<string | null> {
  const t = tauri();
  if (!t) return null;
  return t.core.invoke<string | null>("pick_import_file");
}
