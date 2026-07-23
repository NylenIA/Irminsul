"use server";

import { mkdir, writeFile, rm } from "node:fs/promises";
import path from "node:path";
import { revalidatePath } from "next/cache";
import { callEngine } from "@/server/engine";
import { dataRoot } from "@/server/account";

export type ImportGoodResult =
  | { ok: true; characters: number; weapons: number; artifacts: number }
  | { ok: false; error: string };

const MAX_SIZE = 50 * 1024 * 1024; // 50 Mo — largement au-dessus d'un scan réel.

/**
 * Import du compte DANS l'app (fini le CLI) : le fichier GOOD uploadé est écrit
 * dans la racine de données (desktop : %APPDATA%, dev : <repo>/data), puis le
 * MOTEUR exécute son pipeline d'import existant (validation format GOOD,
 * copie brute read-only, snapshot, normalisation → account/current). Aucune
 * normalisation dupliquée côté web : une seule source de vérité (Python).
 */
export async function importGoodAction(formData: FormData): Promise<ImportGoodResult> {
  const file = formData.get("good");
  if (!(file instanceof File) || file.size === 0) {
    return { ok: false, error: "Choisis d'abord ton fichier de scan (.json)." };
  }
  if (file.size > MAX_SIZE) {
    return { ok: false, error: "Fichier trop volumineux (> 50 Mo) — ce n'est pas un scan GOOD." };
  }

  const text = await file.text();
  // Pré-validation honnête AVANT d'écrire quoi que ce soit : JSON + format GOOD.
  try {
    const parsed = JSON.parse(text) as { format?: string };
    if (parsed?.format !== "GOOD") {
      return {
        ok: false,
        error:
          "Ce fichier n'est pas un export GOOD (champ format ≠ \"GOOD\"). Exporte ton scan depuis InventoryKamera ou Genshin Optimizer.",
      };
    }
  } catch {
    return { ok: false, error: "Fichier illisible : ce n'est pas un JSON valide." };
  }

  const uploadsDir = path.join(dataRoot(), "account", "uploads");
  const uploadPath = path.join(uploadsDir, `good-${Date.now()}.json`);
  try {
    await mkdir(uploadsDir, { recursive: true });
    await writeFile(uploadPath, text, "utf8");
    const res = await callEngine("import-good", { path: uploadPath });
    const imported = (res["import"] ?? {}) as { counts?: Record<string, number> };
    const counts = imported.counts ?? {};
    revalidatePath("/characters");
    revalidatePath("/team-lab");
    revalidatePath("/recommendations");
    return {
      ok: true,
      characters: Number(counts["characters"] ?? 0),
      weapons: Number(counts["weapons"] ?? 0),
      artifacts: Number(counts["artifacts"] ?? 0),
    };
  } catch (error) {
    return {
      ok: false,
      error: `Import refusé par le moteur : ${error instanceof Error ? error.message : "erreur inconnue"}`,
    };
  } finally {
    // Le pipeline moteur garde sa propre copie brute (raw/) : l'upload temporaire est nettoyé.
    await rm(uploadPath, { force: true }).catch(() => {});
  }
}
