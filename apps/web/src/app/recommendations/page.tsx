import { getTeamRepository } from "@irminsul/data-access";
import { RecommendationsClient, type RecoTeamOption } from "./RecommendationsClient";

export const dynamic = "force-dynamic";

export default async function RecommendationsPage(): Promise<React.ReactElement> {
  let teams: RecoTeamOption[] = [];
  try {
    teams = (await getTeamRepository().list()).map((t) => ({ id: t.id, name: t.name }));
  } catch {
    teams = [];
  }
  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 900, margin: "0 auto", display: "grid", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>Recommandations</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Recommandations transparentes, fondées uniquement sur les données réelles de ton compte.
          Chaque conseil montre ses preuves, compromis et données manquantes — aucun impact chiffré inventé.
        </p>
      </header>
      <RecommendationsClient teams={teams} />
    </main>
  );
}
