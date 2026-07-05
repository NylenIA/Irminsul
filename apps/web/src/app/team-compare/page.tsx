import { getTeamRepository } from "@irminsul/data-access";
import { TeamCompareClient, type CompareTeamOption } from "./TeamCompareClient";

export const dynamic = "force-dynamic";

export default async function TeamComparePage(): Promise<React.ReactElement> {
  let teams: CompareTeamOption[] = [];
  try {
    teams = (await getTeamRepository().list()).map((t) => ({
      id: t.id,
      name: t.name,
      members: t.members.slice().sort((a, b) => a.slot - b.slot).map((m) => m.character),
    }));
  } catch {
    teams = [];
  }
  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 1000, margin: "0 auto", display: "grid", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>Comparateur d&apos;équipes</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Comparaison quantitative : deux équipes, deux rotations définies, une cible commune.
          Un verdict de DPS n&apos;est affiché que si les deux rotations sont <strong>complètes</strong> — jamais estimé.
        </p>
      </header>
      <TeamCompareClient teams={teams} />
    </main>
  );
}
