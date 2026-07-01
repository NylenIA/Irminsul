/**
 * Contrat EngineClient — frontière Team Lab ↔ moteur de combat (ADR: docs/architecture/TEAM_LAB_COMBAT_ENGINE_ADR.md).
 *
 * L'UI dépend de CETTE interface, jamais d'une implémentation. Les pourcentages sont des
 * décimaux (46.6% → 0.466). Tout résultat porte sa provenance : rien n'est présenté comme
 * un « vrai DPS » — c'est un calcul déterministe d'un coup isolé, hypothèses visibles.
 */

export interface DirectHitInput {
  /** Multiplicateur de talent (250% → 2.5). */
  scaling: number;
  /** Stat porteuse (ATQ/PV/DÉF finale selon le talent). */
  scalingStat: number;
  flatBaseDamage?: number;
  damageBonus?: number;
  critRate?: number;
  critDamage?: number;
  attackerLevel?: number;
  enemyLevel?: number;
  enemyResistance?: number;
  defenseReduction?: number;
  defenseIgnore?: number;
  amplifyingReactionMultiplier?: number;
  reactionBonus?: number;
  vulnerabilityMultiplier?: number;
}

export interface DirectHitResult {
  rawBase: number;
  nonCrit: number;
  crit: number;
  /** Moyenne pondérée par le taux critique. */
  expected: number;
  defenseMultiplier: number;
  resistanceMultiplier: number;
  expectedCritMultiplier: number;
}

export interface CalculationProvenance {
  /** Implémentation ayant produit le résultat. */
  engine: "ts-port" | "python-sidecar";
  /** Référence de formule (registre des mécaniques Irminsul). */
  formula: "direct_hit@irminsul-damage";
  /** Statut dans le registre des mécaniques. */
  registryStatus: "verified";
  /** Hypothèses non couvertes par ce calcul (affichées à l'utilisateur). */
  assumptions: readonly string[];
}

export interface DirectHitOutcome {
  result: DirectHitResult;
  provenance: CalculationProvenance;
}

/** Frontière stable vers le moteur. Implémentations : TS local (maintenant), sidecar Python (desktop). */
export interface EngineClient {
  calculateDirectHit(input: DirectHitInput): DirectHitOutcome;
}

export const DIRECT_HIT_ASSUMPTIONS = Object.freeze([
  "Coup isolé — pas une rotation ni un DPS d'équipe (gcsim requis pour cela).",
  "Buffs/débuffs à fournir en entrée : rien n'est déduit automatiquement.",
  "Réaction amplifiante fournie explicitement (direction du déclenchement non devinée).",
] as const);
