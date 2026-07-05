"use server";

import path from "node:path";
import {
  compareTeamPerformance,
  normalizeRotation,
  validateRotation,
  type EnemyTarget,
  type RotationAction,
  type TeamComparisonResult,
} from "@irminsul/engine-client";
import { runSidecar, SidecarError } from "@irminsul/engine-client/sidecar";
import { getTeamRepository } from "@irminsul/data-access";

export interface CompareSideInput {
  teamId: string;
  actions: RotationAction[];
}

export type QuantitativeCompareResult =
  | { ok: true; comparison: TeamComparisonResult }
  | { ok: false; kind: "validation_error"; issues: string[] }
  | { ok: false; kind: "engine_error"; message: string };

const SIDECAR = {
  pythonPath:
    process.env["IRMINSUL_PYTHON"] ??
    path.join(process.cwd(), "..", "..", ".venv", "Scripts", "python.exe"),
  scriptPath: path.join(process.cwd(), "..", "..", "scripts", "engine_stdio.py"),
  timeoutMs: 15000,
};

async function runOneRotation(team: string[], actions: RotationAction[], target: EnemyTarget) {
  const raw = await runSidecar(SIDECAR, {
    method: "calculate_rotation",
    params: { team, actions, enemy: { level: target.level, resistance: target.resistance } },
  });
  return normalizeRotation(raw as Parameters<typeof normalizeRotation>[0]);
}

/**
 * Comparaison QUANTITATIVE : deux équipes, deux rotations définies, la MÊME cible.
 * Verdict de DPS uniquement si les deux rotations sont complètes (géré par compareTeamPerformance).
 */
export async function compareTeamsQuantitativeAction(
  left: CompareSideInput,
  right: CompareSideInput,
  target: EnemyTarget,
): Promise<QuantitativeCompareResult> {
  if (left.teamId === right.teamId) {
    return { ok: false, kind: "validation_error", issues: ["Choisis deux équipes différentes."] };
  }
  // Cible bornée (défense en profondeur — même bornes que le moteur).
  if (!(target.level >= 1 && target.level <= 200) || !(target.resistance >= -1 && target.resistance <= 3)) {
    return { ok: false, kind: "validation_error", issues: ["Cible invalide (niveau 1..200, résistance -1..3)."] };
  }

  const repo = getTeamRepository();
  const [tA, tB] = await Promise.all([repo.getById(left.teamId), repo.getById(right.teamId)]);
  if (!tA || !tB) return { ok: false, kind: "engine_error", message: "Équipe introuvable." };

  const membersA = tA.members.slice().sort((a, b) => a.slot - b.slot).map((m) => m.character);
  const membersB = tB.members.slice().sort((a, b) => a.slot - b.slot).map((m) => m.character);

  const issues = [
    ...validateRotation(membersA, left.actions).map((s) => `A: ${s}`),
    ...validateRotation(membersB, right.actions).map((s) => `B: ${s}`),
  ];
  if (issues.length > 0) return { ok: false, kind: "validation_error", issues };

  try {
    const [rotA, rotB] = await Promise.all([
      runOneRotation(membersA, left.actions, target),
      runOneRotation(membersB, right.actions, target),
    ]);
    const comparison = compareTeamPerformance(tA.name, rotA, tB.name, rotB, target);
    return { ok: true, comparison };
  } catch (error) {
    const message = error instanceof SidecarError ? error.message : "Erreur moteur inconnue.";
    return { ok: false, kind: "engine_error", message };
  }
}
