export {
  calculateDirectHit,
  defenseMultiplier,
  LocalEngineClient,
  resistanceMultiplier,
} from "./direct-hit";
export {
  DIRECT_HIT_ASSUMPTIONS,
  ENGINE_CONTRACT_VERSION,
  type CalculationProvenance,
  type DirectHitInput,
  type DirectHitOutcome,
  type DirectHitResult,
  type EngineClient,
} from "./contract";
export {
  buildDirectHitPreview,
  type DirectHitPreview,
  type DirectHitPreviewRequest,
  type DirectHitPreviewResult,
  type PreviewFailureKind,
  type ReactionPreview,
} from "./preview";
export {
  AMPLIFYING_BASE,
  amplifyingMultiplier,
  LEVEL_MULTIPLIER_LV90,
  REACTION_CONTRACT_VERSION,
  REACTION_PROVENANCE,
  TRANSFORMATIVE_BASE,
  transformativeReaction,
  type AmplifyingKind,
  type AmplifyingResult,
  type TransformativeKind,
  type TransformativeResult,
} from "./reactions";
export { normalizePlayerBuild, parseArtifactSets, parseWeaponRef, type PlayerCharacterBuild } from "./player-build";
export {
  FINAL_STATS_CONTRACT_VERSION,
  normalizeFinalStats,
  type FinalCharacterStats,
  type FinalStatCell,
  type FinalStatsResult,
} from "./final-stats";
export {
  ROTATION_CONTRACT_VERSION,
  DAMAGE_KINDS,
  normalizeRotation,
  validateRotation,
  type RotationAction,
  type RotationActionKind,
  type RotationActionResult,
  type RotationResult,
} from "./rotation";
export {
  TEAM_COMPARE_CONTRACT_VERSION,
  compareTeamPerformance,
  type EnemyTarget,
  type TeamComparisonResult,
  type TeamMetricDifference,
  type TeamPerformanceSummary,
} from "./team-compare";
// NOTE : le sidecar (node:child_process) n'est PAS ré-exporté ici — le barrel doit rester
// importable côté client. Serveur : import depuis "@irminsul/engine-client/sidecar".
