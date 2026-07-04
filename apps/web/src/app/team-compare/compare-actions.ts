"use server";

import { getTeamRepository } from "@irminsul/data-access";
import { loadAccountSummary } from "@/server/account";
import {
  TEAM_COMPARE_CONTRACT_VERSION,
  type CompareResult,
  type MemberComparison,
  type TeamComparison,
  type TeamComparisonSide,
} from "./compare-types";

/**
 * Comparaison d'équipes — squelette HONNÊTE (contrat stable pour les recommandations à venir).
 * Compare uniquement ce qui est calculable SANS simulation : composition, éléments, et complétude
 * des données du compte. La comparaison de dégâts/DPS est explicitement marquée « nécessite une
 * rotation définie » — jamais un chiffre inventé.
 */
export async function compareTeamsAction(teamAId: string, teamBId: string): Promise<CompareResult> {
  if (!teamAId || !teamBId) return { ok: false, message: "Deux équipes sont requises." };
  if (teamAId === teamBId) return { ok: false, message: "Choisis deux équipes différentes." };

  const repo = getTeamRepository();
  const [a, b] = await Promise.all([repo.getById(teamAId), repo.getById(teamBId)]);
  if (!a || !b) return { ok: false, message: "Équipe introuvable." };

  const account = await loadAccountSummary();
  const scanByName = new Map(
    (account?.characters ?? []).map((c) => [c.characterId, c] as const),
  );

  const side = (team: NonNullable<typeof a>): TeamComparisonSide => {
    const members: MemberComparison[] = team.members
      .slice()
      .sort((m1, m2) => m1.slot - m2.slot)
      .map((m) => {
        const build = scanByName.get(m.character);
        return {
          character: m.character,
          inScan: !!build,
          level: build?.level,
          hasWeapon: !!build?.weapon,
          artifactPieces: build?.artifactSlots?.length ?? 0,
        };
      });
    const inScan = members.filter((m) => m.inScan).length;
    const completeness: TeamComparisonSide["dataCompleteness"] =
      inScan === 0 ? "none" : inScan === members.length ? "complete" : "partial";
    return { id: team.id, name: team.name, members, membersInScan: inScan, dataCompleteness: completeness };
  };

  const sideA = side(a);
  const sideB = side(b);

  const dimensions: TeamComparison["dimensions"] = [
    { label: "Nombre de membres", a: String(sideA.members.length), b: String(sideB.members.length), computable: true },
    { label: "Membres dans le scan", a: `${sideA.membersInScan}/${sideA.members.length}`, b: `${sideB.membersInScan}/${sideB.members.length}`, computable: true },
    { label: "Complétude des données", a: sideA.dataCompleteness, b: sideB.dataCompleteness, computable: true },
    {
      label: "Dégâts totaux / DPS", a: "—", b: "—", computable: false,
      note: "Nécessite une rotation définie pour chaque équipe (moteur rotation/1.0). Non calculé — jamais estimé.",
    },
  ];

  return {
    ok: true,
    comparison: {
      contractVersion: TEAM_COMPARE_CONTRACT_VERSION,
      a: sideA,
      b: sideB,
      dimensions,
      assumptions: [
        "Comparaison structurelle uniquement (composition + complétude du compte).",
        "La comparaison de dégâts exige une rotation par équipe — à venir (contrat rotation/1.0 déjà disponible).",
      ],
      warnings: [
        ...(sideA.dataCompleteness !== "complete" ? [`${sideA.name} : données de compte partielles.`] : []),
        ...(sideB.dataCompleteness !== "complete" ? [`${sideB.name} : données de compte partielles.`] : []),
      ],
    },
  };
}
