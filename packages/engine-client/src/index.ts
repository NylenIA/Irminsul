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
  ADDITIVE_BASE,
  additiveReaction,
  AMPLIFYING_BASE,
  amplifyingMultiplier,
  LEVEL_MULTIPLIER_LV90,
  REACTION_CONTRACT_VERSION,
  REACTION_PROVENANCE,
  TRANSFORMATIVE_BASE,
  transformativeReaction,
  LUNAR_BASE,
  LUNAR_CONTRIBUTION_WEIGHTS,
  lunarChargedReaction,
  lunarEmBonus,
  lunarReaction,
  type AdditiveKind,
  type AdditiveResult,
  type AmplifyingKind,
  type AmplifyingResult,
  type LunarChargedResult,
  type LunarContributorBreakdown,
  type LunarContributorInput,
  type LunarKind,
  type TransformativeKind,
  type TransformativeResult,
} from "./reactions";
export { normalizePlayerBuild, parseArtifactSets, parseWeaponRef, type PlayerCharacterBuild } from "./player-build";
export {
  GCSIM_CONFIG_CONTRACT_VERSION,
  normalizeGcsimKey,
  teamToGcsimSkeleton,
  type GcsimSkeletonMember,
} from "./gcsim-config";
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
export {
  RECOMMENDATIONS_CONTRACT_VERSION,
  buildRecommendations,
  type RecommendationItem,
  type RecommendationObjective,
  type RecommendationRequest,
  type RecommendationResult,
  type RecommendationType,
  type TeamForReco,
} from "./recommendations";
export {
  EXPORT_FORMAT_VERSION,
  MAX_IMPORT_BYTES,
  buildExport,
  checksumOf,
  planImport,
  validateImport,
  type ExportFile,
  type ExportableTeam,
  type ImportPlan,
  type ImportValidation,
} from "./import-export";
// NOTE : le sidecar (node:child_process) n'est PAS ré-exporté ici — le barrel doit rester
// importable côté client. Serveur : import depuis "@irminsul/engine-client/sidecar".
