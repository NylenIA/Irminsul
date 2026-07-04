/**
 * Contrat de rotation `rotation/1.0` + validation de timeline PURE (avant le moteur Python).
 * La validation TS attrape les erreurs de structure côté client (rapide, testable) ; le calcul
 * de dégâts (coefficients + stats réels) reste dans le moteur Python via le sidecar.
 * Aucun DPS ici : cette couche ne fait que valider et typer.
 */
export const ROTATION_CONTRACT_VERSION = "rotation/1.0";

export type RotationActionKind =
  | "swap"
  | "normal_attack"
  | "charged_attack"
  | "plunging_attack"
  | "skill"
  | "burst"
  | "wait";

export const DAMAGE_KINDS: ReadonlySet<RotationActionKind> = new Set([
  "normal_attack",
  "charged_attack",
  "plunging_attack",
  "skill",
  "burst",
]);

export interface RotationAction {
  id: string;
  actorId: string;
  kind: RotationActionKind;
  startTime: number;
  duration: number;
  talentSlot?: string;
  talentLabel?: string;
  talentLevel?: number;
  targetCount?: number;
}

export interface RotationActionResult {
  actorId: string;
  kind: RotationActionKind;
  complete: boolean;
  damage: number | null;
  warnings: string[];
  provenance: Record<string, unknown>;
  coefficient?: number;
  scaling_stat_atk?: number;
}

export interface RotationResult {
  contractVersion: string;
  duration: number;
  actions: RotationActionResult[];
  totalDamage: number | null;
  averageDamagePerSecond: number | null;
  damageByCharacter: Record<string, number>;
  complete: boolean;
  assumptions: string[];
  warnings: string[];
  provenance: Record<string, unknown>;
  confidence: "high" | "medium" | "low";
  note?: string;
}

const MAX_ACTIONS = 200;
const MAX_TIME = 3600;

function finite(x: unknown): x is number {
  return typeof x === "number" && Number.isFinite(x);
}

/**
 * Validation PURE de la timeline (mêmes règles que le moteur Python — défense en profondeur).
 * Retourne la liste des problèmes ; vide = valide.
 */
export function validateRotation(team: string[], actions: RotationAction[]): string[] {
  const issues: string[] = [];
  if (!Array.isArray(team) || team.length === 0) issues.push("Équipe vide.");
  if (!Array.isArray(actions) || actions.length === 0) {
    issues.push("Rotation vide : au moins une action requise.");
    return issues;
  }
  if (actions.length > MAX_ACTIONS) issues.push(`Trop d'actions (> ${MAX_ACTIONS}).`);
  const teamSet = new Set(team);
  let prevEnd = 0;
  actions.forEach((a, i) => {
    if (!DAMAGE_KINDS.has(a.kind) && a.kind !== "swap" && a.kind !== "wait") {
      issues.push(`Action ${i + 1} : type inconnu (${a.kind}).`);
    }
    if (!a.actorId || !teamSet.has(a.actorId)) {
      issues.push(`Action ${i + 1} : acteur absent de l'équipe.`);
    }
    if (!finite(a.startTime) || a.startTime < 0) issues.push(`Action ${i + 1} : début invalide (≥ 0).`);
    if (!finite(a.duration) || a.duration < 0) issues.push(`Action ${i + 1} : durée invalide (≥ 0).`);
    if (finite(a.startTime) && finite(a.duration)) {
      if (a.startTime + a.duration > MAX_TIME) issues.push(`Action ${i + 1} : dépasse ${MAX_TIME}s.`);
      if (a.startTime + 1e-9 < prevEnd) issues.push(`Action ${i + 1} : chevauchement temporel.`);
      prevEnd = a.startTime + a.duration;
    }
  });
  return issues;
}

interface RawRotation {
  contract_version?: string;
  duration?: number;
  actions?: RotationActionResult[];
  total_damage?: number | null;
  average_damage_per_second?: number | null;
  damage_by_character?: Record<string, number>;
  complete?: boolean;
  assumptions?: string[];
  warnings?: string[];
  provenance?: Record<string, unknown>;
  confidence?: "high" | "medium" | "low";
  note?: string;
}

/** Adapte la sortie brute du moteur Python en DTO typé (camelCase), sans réinterpréter les chiffres. */
export function normalizeRotation(raw: RawRotation): RotationResult {
  return {
    contractVersion: raw.contract_version ?? ROTATION_CONTRACT_VERSION,
    duration: finite(raw.duration) ? raw.duration : 0,
    actions: Array.isArray(raw.actions) ? raw.actions : [],
    totalDamage: finite(raw.total_damage) ? raw.total_damage! : null,
    averageDamagePerSecond: finite(raw.average_damage_per_second)
      ? raw.average_damage_per_second!
      : null,
    damageByCharacter: raw.damage_by_character ?? {},
    complete: raw.complete === true,
    assumptions: raw.assumptions ?? [],
    warnings: raw.warnings ?? [],
    provenance: raw.provenance ?? {},
    confidence: raw.confidence ?? "low",
    note: raw.note,
  };
}
