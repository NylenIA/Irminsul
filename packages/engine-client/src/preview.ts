/**
 * Aperçu de coup direct — orchestration pure (validation, défauts, conversion %→décimal,
 * appel moteur, provenance). AUCUNE formule ici (elle vit dans direct-hit.ts, parité Python
 * prouvée par goldens). Ce module est appelé par la Server Action ; l'UI n'en dépend que
 * par ses types. Un aperçu N'EST PAS un DPS de rotation — hypothèses toujours jointes.
 */
import { ENGINE_CONTRACT_VERSION, type DirectHitOutcome } from "./contract";
import { LocalEngineClient } from "./direct-hit";

/** Entrées utilisateur en POURCENTAGES (250 = 250 %) — plus lisible côté formulaire. */
export interface DirectHitPreviewRequest {
  character: string;
  /** Multiplicateur de talent en % (ex. 250). REQUIS. */
  scalingPct: number | null;
  /** Stat porteuse finale (ATQ/PV/DÉF). REQUIS. */
  scalingStat: number | null;
  critRatePct?: number | null;
  critDamagePct?: number | null;
  damageBonusPct?: number | null;
  enemyLevel?: number | null;
  enemyResistancePct?: number | null;
  attackerLevel?: number | null;
}

export interface DirectHitPreview {
  character: string;
  outcome: DirectHitOutcome;
  contractVersion: string;
  /** Champs non fournis → valeur par défaut du moteur (transparence). */
  defaultsUsed: string[];
  /** Paramètres effectivement utilisés (décimaux), pour affichage honnête. */
  parameters: Record<string, number>;
  confidence: {
    level: "haute";
    reason: "Formule au statut « verified » du registre des mécaniques (goldens croisés en jeu).";
  };
}

export type PreviewFailureKind = "insufficient_data" | "validation_error" | "engine_error";

export type DirectHitPreviewResult =
  | { ok: true; preview: DirectHitPreview }
  | { ok: false; kind: PreviewFailureKind; issues: string[] };

const DEFAULTS = Object.freeze({
  critRatePct: 5,
  critDamagePct: 50,
  damageBonusPct: 0,
  enemyLevel: 100,
  enemyResistancePct: 10,
  attackerLevel: 90,
});

function isMissing(value: number | null | undefined): value is null | undefined {
  return value === null || value === undefined || Number.isNaN(value);
}

function finiteIn(value: number, min: number, max: number): boolean {
  return Number.isFinite(value) && value >= min && value <= max;
}

export function buildDirectHitPreview(request: DirectHitPreviewRequest): DirectHitPreviewResult {
  // 1) Données requises absentes → insufficient_data (jamais de valeur inventée).
  const missing: string[] = [];
  if (!request.character || request.character.trim().length === 0) missing.push("character");
  if (isMissing(request.scalingPct)) missing.push("scalingPct");
  if (isMissing(request.scalingStat)) missing.push("scalingStat");
  if (missing.length > 0) {
    return { ok: false, kind: "insufficient_data", issues: missing };
  }

  // 2) Validation stricte (bornes larges mais finies — pas de NaN/Infinity vers le moteur).
  const issues: string[] = [];
  const scalingPct = request.scalingPct as number;
  const scalingStat = request.scalingStat as number;
  if (!finiteIn(scalingPct, 0, 10000)) issues.push("scalingPct doit être entre 0 et 10000 (%).");
  if (!finiteIn(scalingStat, 0, 1000000)) issues.push("scalingStat doit être entre 0 et 1000000.");

  const defaultsUsed: string[] = [];
  const pick = (key: keyof typeof DEFAULTS): number => {
    const raw = request[key];
    if (isMissing(raw)) {
      defaultsUsed.push(key);
      return DEFAULTS[key];
    }
    return raw;
  };
  const critRatePct = pick("critRatePct");
  const critDamagePct = pick("critDamagePct");
  const damageBonusPct = pick("damageBonusPct");
  const enemyLevel = pick("enemyLevel");
  const enemyResistancePct = pick("enemyResistancePct");
  const attackerLevel = pick("attackerLevel");

  if (!finiteIn(critRatePct, 0, 100)) issues.push("critRatePct doit être entre 0 et 100.");
  if (!finiteIn(critDamagePct, 0, 1000)) issues.push("critDamagePct doit être entre 0 et 1000.");
  if (!finiteIn(damageBonusPct, -100, 1000)) issues.push("damageBonusPct doit être entre -100 et 1000.");
  if (!finiteIn(enemyLevel, 1, 200)) issues.push("enemyLevel doit être entre 1 et 200.");
  if (!finiteIn(enemyResistancePct, -100, 300)) issues.push("enemyResistancePct doit être entre -100 et 300.");
  if (!finiteIn(attackerLevel, 1, 100)) issues.push("attackerLevel doit être entre 1 et 100.");
  if (issues.length > 0) {
    return { ok: false, kind: "validation_error", issues };
  }

  // 3) Conversion % → décimal, puis moteur (RangeError → engine_error typée).
  const parameters = {
    scaling: scalingPct / 100,
    scalingStat,
    critRate: critRatePct / 100,
    critDamage: critDamagePct / 100,
    damageBonus: damageBonusPct / 100,
    enemyLevel,
    enemyResistance: enemyResistancePct / 100,
    attackerLevel,
  };
  try {
    const outcome = new LocalEngineClient().calculateDirectHit(parameters);
    return {
      ok: true,
      preview: {
        character: request.character.trim(),
        outcome,
        contractVersion: ENGINE_CONTRACT_VERSION,
        defaultsUsed,
        parameters,
        confidence: {
          level: "haute",
          reason:
            "Formule au statut « verified » du registre des mécaniques (goldens croisés en jeu).",
        },
      },
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Erreur moteur inconnue.";
    return { ok: false, kind: "engine_error", issues: [message] };
  }
}
