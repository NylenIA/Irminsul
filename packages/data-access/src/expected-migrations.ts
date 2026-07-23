import { MIGRATIONS_BUNDLE } from "./migrations-bundle";

// Migrations Prisma attendues par CETTE version de l'application : dérivées du
// bundle embarqué (lui-même miroir de `prisma/migrations/`, cf. migrations-bundle.ts).
// Utilisé par la détection de dérive (schema-drift.ts). La synchro dossier <-> bundle
// est garantie par `tests/expected-migrations.test.ts`.
export const EXPECTED_MIGRATIONS: readonly string[] = MIGRATIONS_BUNDLE.map((m) => m.name);
