import { getTeamRepository } from "@irminsul/data-access";
import { TeamCompareClient, type CompareTeamOption } from "./TeamCompareClient";

export const dynamic = "force-dynamic";

export default async function TeamComparePage(): Promise<React.ReactElement> {
  let teams: CompareTeamOption[] = [];
  try {
    teams = (await getTeamRepository().list()).map((t) => ({ id: t.id, name: t.name }));
  } catch {
    teams = [];
  }
  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 900, margin: "0 auto", display: "grid", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>Comparateur d&apos;équipes</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Comparaison structurelle honnête. La comparaison de dégâts arrivera via le moteur de
          rotations — aucun chiffre n&apos;est estimé à ta place.
        </p>
      </header>
      <TeamCompareClient teams={teams} />
    </main>
  );
}
