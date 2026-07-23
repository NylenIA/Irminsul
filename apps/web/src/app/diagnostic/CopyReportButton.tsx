"use client";

import { useState } from "react";
import { Button } from "@irminsul/ui";
import type { DiagnosticReport } from "./diag-actions";

/** Copie un rapport JSON sanitizé (déjà masqué côté serveur — aucun secret/nonce/token). */
export function CopyReportButton({ report }: { report: DiagnosticReport }): React.ReactElement {
  const [copied, setCopied] = useState(false);
  return (
    <div>
      <Button
        onClick={() => {
          navigator.clipboard
            .writeText(JSON.stringify(report, null, 2))
            .then(() => { setCopied(true); setTimeout(() => setCopied(false), 2500); });
        }}
      >
        {copied ? "Rapport copié ✓" : "Copier le rapport de diagnostic"}
      </Button>
    </div>
  );
}
