// Détection de dérive de schéma pour la base LOCALE (SQLite).
//
// Problème couvert : côté desktop, la base utilisateur (%APPDATA%) est initialisée
// par COPIE d'un template pré-migré au 1er lancement et n'est jamais réécrite. Le CLI
// Prisma n'étant pas embarqué, une future migration de schéma ne serait pas appliquée
// à une base existante -> l'app casserait silencieusement. Cette primitive DÉTECTE ce
// retard pour permettre un message honnête (ré-import de l'export versionné) au lieu
// d'un crash cryptique. Elle n'APPLIQUE aucune migration (décision d'archi séparée).

import type { PrismaClient } from "@prisma/client";

export type SchemaDriftStatus = "ok" | "drift" | "unknown";

export interface SchemaDriftReport {
  /** ok = à jour ; drift = base en retard ; unknown = historique illisible. */
  status: SchemaDriftStatus;
  /** Migrations effectivement appliquées dans la base (triées). */
  applied: string[];
  /** Migrations attendues par cette version de l'app (triées). */
  expected: string[];
  /** Migrations attendues absentes de la base (vide si ok/unknown). */
  missing: string[];
  /** Résumé lisible, sans secret ni chemin (sûr pour un rapport de diagnostic). */
  detail: string;
}

interface MigrationRow {
  migration_name: string;
}

/** Sous-ensemble minimal de PrismaClient requis (facilite tests et injection). */
export type RawQueryClient = Pick<PrismaClient, "$queryRawUnsafe">;

/**
 * Compare les migrations appliquées (`_prisma_migrations`, terminées) aux migrations
 * attendues. SQL statique (aucune interpolation) -> pas d'injection.
 */
export async function checkSchemaDrift(
  db: RawQueryClient,
  expected: readonly string[],
): Promise<SchemaDriftReport> {
  const expectedSorted = [...expected].sort();

  let rows: MigrationRow[];
  try {
    rows = await db.$queryRawUnsafe<MigrationRow[]>(
      "SELECT migration_name FROM _prisma_migrations WHERE finished_at IS NOT NULL",
    );
  } catch {
    // Table absente ou illisible : on ne peut pas conclure. Honnête = "unknown".
    return {
      status: "unknown",
      applied: [],
      expected: expectedSorted,
      missing: [],
      detail: "Historique de migrations introuvable (_prisma_migrations absent) : schéma non vérifiable.",
    };
  }

  const applied = rows
    .map((r) => r.migration_name)
    .filter((name): name is string => typeof name === "string")
    .sort();
  const appliedSet = new Set(applied);
  const missing = expectedSorted.filter((name) => !appliedSet.has(name));

  if (missing.length > 0) {
    return {
      status: "drift",
      applied,
      expected: expectedSorted,
      missing,
      detail: `Base en retard de ${missing.length} migration(s) : ${missing.join(", ")}. Ré-importe ton export pour repartir d'un schéma à jour.`,
    };
  }

  return {
    status: "ok",
    applied,
    expected: expectedSorted,
    missing: [],
    detail: `Schéma à jour (${applied.length} migration(s) appliquée(s)).`,
  };
}
