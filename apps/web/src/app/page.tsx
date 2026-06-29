export default function Home(): React.ReactElement {
  return (
    <main style={{ padding: "3rem", maxWidth: "60ch", margin: "0 auto" }}>
      <h1>Irminsul — Archive astrale</h1>
      <p>
        Socle web (Next.js 16, App Router, TypeScript strict). L&apos;écran pilote
        « Laboratoire d&apos;équipes » sera branché au moteur déterministe via une
        interface stable (<code>packages/engine-client</code>).
      </p>
      <p>
        Aucune donnée factice n&apos;est affichée : tant que le pont moteur n&apos;est pas
        disponible sur cette branche, les surfaces dépendantes des données restent vides ou
        explicitement marquées « mock isolé ».
      </p>
    </main>
  );
}
