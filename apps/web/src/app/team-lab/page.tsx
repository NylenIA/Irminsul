import { getTeamRepository, type SavedTeamDTO } from "@irminsul/data-access";
import { CHARACTERS } from "@/lib/roster";
import { TeamLabClient } from "./TeamLabClient";

// Rendu à la requête (la base locale n'est pas interrogée au build).
export const dynamic = "force-dynamic";

export default async function TeamLabPage(): Promise<React.ReactElement> {
  let teams: SavedTeamDTO[] = [];
  let loadError = false;
  try {
    teams = await getTeamRepository().list();
  } catch {
    loadError = true;
  }
  return <TeamLabClient initialTeams={teams} roster={CHARACTERS} loadError={loadError} />;
}
