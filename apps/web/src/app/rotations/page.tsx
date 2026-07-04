import { getTeamRepository } from "@irminsul/data-access";
import { RotationsClient, type TeamOption } from "./RotationsClient";

export const dynamic = "force-dynamic";

export default async function RotationsPage(): Promise<React.ReactElement> {
  let teams: TeamOption[] = [];
  try {
    const saved = await getTeamRepository().list();
    teams = saved.map((t) => ({
      id: t.id,
      name: t.name,
      members: t.members
        .slice()
        .sort((a, b) => a.slot - b.slot)
        .map((m) => m.character),
    }));
  } catch {
    teams = [];
  }

  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 1000, margin: "0 auto", display: "grid", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>Rotations</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Rotation chiffrée déterministe : coefficients de talent réels × stats finales réelles.
          Le DPS n&apos;est affiché que si la rotation est <strong>complète et prouvée</strong> — jamais estimé.
        </p>
      </header>
      <RotationsClient teams={teams} />
    </main>
  );
}
