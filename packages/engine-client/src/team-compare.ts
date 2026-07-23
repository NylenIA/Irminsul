/**
 * Comparateur d'équipes QUANTITATIF `team-compare/1.0` — comparaison PURE de deux résultats de
 * rotation (`rotation/1.0`) calculés contre la MÊME cible. Aucun chiffre inventé : un verdict de
 * DPS n'est émis que si les deux rotations sont complètes, comparables et sourcées.
 */
import type { RotationResult } from "./rotation";

export const TEAM_COMPARE_CONTRACT_VERSION = "team-compare/1.0";

export interface EnemyTarget {
  level: number;
  resistance: number;
  count: number;
}

export interface TeamPerformanceSummary {
  teamName: string;
  duration: number;
  totalDamage: number | null;
  averageDamagePerSecond: number | null;
  damageByCharacter: Record<string, number>;
  actionCount: number;
  complete: boolean;
  confidence: "high" | "medium" | "low";
  warnings: string[];
}

export interface TeamMetricDifference {
  metric: string;
  left: number | null;
  right: number | null;
  absolute: number | null;
  relativePct: number | null;
  computable: boolean;
  winner: "left" | "right" | "tie" | null;
}

export interface TeamComparisonResult {
  contractVersion: string;
  left: TeamPerformanceSummary;
  right: TeamPerformanceSummary;
  target: EnemyTarget;
  differences: TeamMetricDifference[];
  verdict: string;
  assumptions: string[];
  warnings: string[];
  confidence: "high" | "medium" | "low";
  complete: boolean;
}

function summary(name: string, r: RotationResult): TeamPerformanceSummary {
  return {
    teamName: name,
    duration: r.duration,
    totalDamage: r.totalDamage,
    averageDamagePerSecond: r.averageDamagePerSecond,
    damageByCharacter: r.damageByCharacter,
    actionCount: r.actions.length,
    complete: r.complete,
    confidence: r.confidence,
    warnings: r.warnings,
  };
}

function diff(
  metric: string,
  left: number | null,
  right: number | null,
  higherIsBetter = true,
): TeamMetricDifference {
  if (left === null || right === null || !Number.isFinite(left) || !Number.isFinite(right)) {
    return { metric, left, right, absolute: null, relativePct: null, computable: false, winner: null };
  }
  const absolute = left - right;
  const base = Math.max(Math.abs(left), Math.abs(right));
  const relativePct = base > 0 ? (absolute / base) * 100 : 0;
  let winner: TeamMetricDifference["winner"] = "tie";
  if (absolute !== 0) {
    const leftBetter = higherIsBetter ? absolute > 0 : absolute < 0;
    winner = leftBetter ? "left" : "right";
  }
  return { metric, left, right, absolute, relativePct, computable: true, winner };
}

/**
 * Compare deux rotations calculées contre la MÊME cible.
 * Verdict quantitatif SEULEMENT si les deux sont complètes ; sinon comparaison partielle honnête.
 */
export function compareTeamPerformance(
  leftName: string,
  left: RotationResult,
  rightName: string,
  right: RotationResult,
  target: EnemyTarget,
): TeamComparisonResult {
  const l = summary(leftName, left);
  const r = summary(rightName, right);

  const bothComplete = l.complete && r.complete;
  // Audit Codex Low : ne JAMAIS produire un gagnant de métrique si une rotation est incomplète,
  // même si ses valeurs sont finies. Le contrat exporté est ainsi aussi strict que le verdict.
  const metrics: [string, number | null, number | null, boolean][] = [
    ["DPS moyen", l.averageDamagePerSecond, r.averageDamagePerSecond, true],
    ["Dégâts totaux", l.totalDamage, r.totalDamage, true],
    ["Durée (s)", l.duration, r.duration, false],
  ];
  const differences: TeamMetricDifference[] = metrics.map(([metric, left, right, higher]) =>
    bothComplete
      ? diff(metric, left, right, higher)
      : { metric, left, right, absolute: null, relativePct: null, computable: false, winner: null },
  );

  let verdict: string;
  let confidence: "high" | "medium" | "low";
  if (!bothComplete) {
    verdict =
      "Aucun verdict quantitatif fiable — au moins une rotation est incomplète (données insuffisantes).";
    confidence = "low";
  } else {
    const dpsDiff = differences[0]!;
    if (dpsDiff.computable && dpsDiff.winner && dpsDiff.winner !== "tie") {
      const winName = dpsDiff.winner === "left" ? leftName : rightName;
      verdict = `${winName} a un DPS supérieur de ${Math.abs(dpsDiff.relativePct ?? 0).toFixed(1)} % sur cette cible et ces rotations.`;
      confidence = "high";
    } else {
      verdict = "DPS équivalent sur cette cible et ces rotations.";
      confidence = "high";
    }
  }

  const warnings = [...new Set([...l.warnings, ...r.warnings])];
  return {
    contractVersion: TEAM_COMPARE_CONTRACT_VERSION,
    left: l,
    right: r,
    target,
    differences,
    verdict,
    assumptions: [
      "Les deux rotations sont évaluées contre la MÊME cible (niveau, résistance, nombre).",
      "Comparaison valable uniquement pour les rotations et cibles saisies — pas un classement méta global.",
      "DPS comparé seulement si les deux rotations sont complètes (coefficients + stats finales réels).",
    ],
    warnings,
    confidence,
    complete: bothComplete,
  };
}
