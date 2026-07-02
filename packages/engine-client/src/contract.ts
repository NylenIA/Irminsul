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

/**
 * Frontière stable vers le moteur. Implémentations : TS local (maintenant), sidecar Python (desktop).
 *
 * Invariants et normalisations (identiques au moteur Python, source de vérité) :
 * - `scaling`/`scalingStat` ≥ 0 et multiplicateurs (`amplifyingReactionMultiplier`,
 *   `vulnerabilityMultiplier`) > 0, sinon **RangeError** (équivalent du ValueError Python) ;
 * - clamps silencieux : `critRate` → [0, 1] ; `critDamage` → ≥ 0 ; `reactionBonus` → ≥ 0 ;
 *   `defenseReduction`/`defenseIgnore` → [0, 0.99] ;
 * - résistance par branches : R < 0 → 1 − R/2 ; 0 ≤ R < 0.75 → 1 − R ; R ≥ 0.75 → 1/(4R + 1) ;
 * - les entrées non finies (NaN/Infinity) ne sont PAS filtrées — comportement identique au
 *   moteur Python ; la validation amont incombe à l'appelant (formulaires UI).
 */
export interface EngineClient {
  calculateDirectHit(input: DirectHitInput): DirectHitOutcome;
}

/** Version du contrat de calcul — affichée dans l'UI ; un désaccord client/serveur = stale_contract. */
export const ENGINE_CONTRACT_VERSION = "direct-hit/1.0";

export const DIRECT_HIT_ASSUMPTIONS = Object.freeze([
  "Coup isolé — pas une rotation ni un DPS d'équipe (gcsim requis pour cela).",
  "Buffs/débuffs à fournir en entrée : rien n'est déduit automatiquement.",
  "Réaction amplifiante fournie explicitement (direction du déclenchement non devinée).",
  "Entrées hors bornes normalisées par clamps (crit 0–1, réduction DEF 0–0.99) — voir contrat.",
] as const);
