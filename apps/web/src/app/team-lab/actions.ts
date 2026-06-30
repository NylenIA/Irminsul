"use server";

import { revalidatePath } from "next/cache";
import {
  getTeamRepository,
  TeamRepositoryValidationError,
  type SaveTeamInput,
} from "@irminsul/data-access";

export type ActionResult = { ok: true } | { ok: false; error: string };

export async function saveTeamAction(input: SaveTeamInput): Promise<ActionResult> {
  try {
    await getTeamRepository().save(input);
    revalidatePath("/team-lab");
    return { ok: true };
  } catch (e) {
    if (e instanceof TeamRepositoryValidationError) {
      return { ok: false, error: e.message };
    }
    return { ok: false, error: "Échec de la sauvegarde (base locale)." };
  }
}

export async function deleteTeamAction(id: string): Promise<ActionResult> {
  try {
    await getTeamRepository().delete(id);
    revalidatePath("/team-lab");
    return { ok: true };
  } catch {
    return { ok: false, error: "Échec de la suppression." };
  }
}
