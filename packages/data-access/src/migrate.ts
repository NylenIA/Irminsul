// Runner de migration au démarrage pour la base LOCALE (SQLite).
//
// Ferme le gap "migration-on-update" desktop : la base %APPDATA% est initialisée
// par copie d'un template pré-migré et jamais réécrite ; le CLI Prisma n'est pas
// embarqué. Ce runner applique, au boot, les migrations du bundle ABSENTES de la
// base, de façon IDEMPOTENTE et TRANSACTIONNELLE (chaque migration tout-ou-rien).
//
// Sûreté : ne touche QUE les bases gérées par Prisma (table `_prisma_migrations`
// présente) ; ne supprime/réécrit jamais de données existantes ; en échec, la
// transaction est annulée (aucune application partielle). Sur les bases déjà à
// jour (cas actuel : template complet) c'est un strict no-op.

import type { PrismaClient } from "@prisma/client";
import { createHash, randomUUID } from "node:crypto";
import { MIGRATIONS_BUNDLE, type BundledMigration } from "./migrations-bundle";

export type MigrateStatus = "applied" | "noop" | "skipped-unmanaged";

export interface MigrateResult {
  /** applied = migrations posées ; noop = déjà à jour ; skipped-unmanaged = base non-Prisma. */
  status: MigrateStatus;
  applied: string[];
  alreadyPresent: string[];
}

/** Découpe un fichier de migration en instructions exécutables (';' en fin de ligne). */
function splitSqlStatements(sql: string): string[] {
  return sql
    .split(/;\s*(?:\r?\n|$)/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export async function applyPendingMigrations(
  db: PrismaClient,
  bundle: readonly BundledMigration[] = MIGRATIONS_BUNDLE,
): Promise<MigrateResult> {
  let recorded: { migration_name: string }[];
  try {
    recorded = await db.$queryRawUnsafe<{ migration_name: string }[]>(
      "SELECT migration_name FROM _prisma_migrations WHERE finished_at IS NOT NULL",
    );
  } catch {
    // Base non gérée par Prisma (table absente) : ne rien tenter (évite tout dégât).
    return { status: "skipped-unmanaged", applied: [], alreadyPresent: [] };
  }

  const present = new Set(recorded.map((r) => r.migration_name));
  const pending = bundle.filter((m) => !present.has(m.name));
  if (pending.length === 0) {
    return { status: "noop", applied: [], alreadyPresent: [...present].sort() };
  }

  const applied: string[] = [];
  for (const migration of pending) {
    const statements = splitSqlStatements(migration.sql);
    const checksum = createHash("sha256").update(migration.sql).digest("hex");
    // Tout-ou-rien : si une instruction échoue, la migration entière est annulée
    // (SQLite supporte le DDL transactionnel) et rien n'est enregistré.
    await db.$transaction(async (tx) => {
      for (const statement of statements) {
        await tx.$executeRawUnsafe(statement);
      }
      await tx.$executeRawUnsafe(
        "INSERT INTO _prisma_migrations (id, checksum, migration_name, started_at, finished_at, applied_steps_count) VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)",
        randomUUID(),
        checksum,
        migration.name,
        statements.length,
      );
    });
    applied.push(migration.name);
  }

  return { status: "applied", applied, alreadyPresent: [...present].sort() };
}
