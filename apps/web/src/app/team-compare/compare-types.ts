/** Types + version de contrat du comparateur (module neutre — importable client & serveur). */
export const TEAM_COMPARE_CONTRACT_VERSION = "team-compare/0.1";

export interface MemberComparison {
  character: string;
  element?: string;
  inScan: boolean;
  level?: number;
  hasWeapon: boolean;
  artifactPieces: number;
}

export interface TeamComparisonSide {
  id: string;
  name: string;
  members: MemberComparison[];
  membersInScan: number;
  dataCompleteness: "complete" | "partial" | "none";
}

export interface TeamComparison {
  contractVersion: string;
  a: TeamComparisonSide;
  b: TeamComparisonSide;
  dimensions: { label: string; a: string; b: string; computable: boolean; note?: string }[];
  assumptions: string[];
  warnings: string[];
}

export type CompareResult =
  | { ok: true; comparison: TeamComparison }
  | { ok: false; message: string };
