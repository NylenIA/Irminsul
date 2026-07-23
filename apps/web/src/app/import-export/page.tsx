import { ImportExportClient } from "./ImportExportClient";

export const dynamic = "force-dynamic";

export default function ImportExportPage(): React.ReactElement {
  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 820, margin: "0 auto", display: "grid", gap: 16 }}>
      <header>
        <h1 style={{ margin: 0 }}>Import / Export</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Sauvegarde et restauration de tes équipes (format versionné <code>irminsul-export/1.0</code>).
          Aucun secret n&apos;est exporté ; l&apos;import montre un aperçu avant écriture et s&apos;applique de
          façon transactionnelle (tout ou rien).
        </p>
      </header>
      <ImportExportClient />
    </main>
  );
}
