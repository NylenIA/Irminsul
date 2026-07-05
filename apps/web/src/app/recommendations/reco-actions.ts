"use server";

import {
  buildRecommendations,
  type RecommendationRequest,
  type RecommendationResult,
} from "@irminsul/engine-client";
import { getTeamRepository } from "@irminsul/data-access";
import { loadAccountSummary } from "@/server/account";

/**
 * Recommandations transparentes — résout les données RÉELLES côté serveur (scan + équipes) puis
 * appelle le moteur déterministe `buildRecommendations`. Aucune donnée web, aucun leak, aucun
 * chiffre inventé ; provenance curée (jamais de chemin local).
 */
export async function getRecommendationsAction(
  request: Omit<RecommendationRequest, "availableCharacterIds">,
): Promise<RecommendationResult> {
  const account = await loadAccountSummary();
  const builds = account?.characters ?? [];
  let teams: { id: string; name: string; members: string[] }[] = [];
  try {
    teams = (await getTeamRepository().list()).map((t) => ({
      id: t.id,
      name: t.name,
      members: t.members.slice().sort((a, b) => a.slot - b.slot).map((m) => m.character),
    }));
  } catch {
    teams = [];
  }
  const full: RecommendationRequest = {
    ...request,
    availableCharacterIds: builds.map((b) => b.characterId),
  };
  return buildRecommendations(
    full,
    builds,
    teams,
    account ? { source: account.scannerName, importedAt: account.importedAt } : null,
  );
}
