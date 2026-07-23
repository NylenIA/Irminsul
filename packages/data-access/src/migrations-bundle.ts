// GÉNÉRÉ par scripts/gen-migrations-bundle.mjs — NE PAS ÉDITER À LA MAIN.
// Miroir embarqué des migrations Prisma (dossier prisma/migrations/), disponible
// à l'exécution y compris dans le bundle desktop. Régénérer après toute migration :
//   node scripts/gen-migrations-bundle.mjs
// La synchro dossier <-> bundle est vérifiée par tests/expected-migrations.test.ts.

export interface BundledMigration {
  readonly name: string;
  readonly sql: string;
}

export const MIGRATIONS_BUNDLE: readonly BundledMigration[] = [
  { name: "20260630045245_init_local_app_data", sql: "-- CreateTable\nCREATE TABLE \"AppSetting\" (\n    \"key\" TEXT NOT NULL PRIMARY KEY,\n    \"value\" TEXT NOT NULL,\n    \"updatedAt\" DATETIME NOT NULL\n);\n\n-- CreateTable\nCREATE TABLE \"SavedTeam\" (\n    \"id\" TEXT NOT NULL PRIMARY KEY,\n    \"name\" TEXT NOT NULL,\n    \"carry\" TEXT,\n    \"notes\" TEXT,\n    \"createdAt\" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n    \"updatedAt\" DATETIME NOT NULL\n);\n\n-- CreateTable\nCREATE TABLE \"SavedTeamMember\" (\n    \"id\" TEXT NOT NULL PRIMARY KEY,\n    \"teamId\" TEXT NOT NULL,\n    \"character\" TEXT NOT NULL,\n    \"role\" TEXT,\n    \"slot\" INTEGER NOT NULL,\n    CONSTRAINT \"SavedTeamMember_teamId_fkey\" FOREIGN KEY (\"teamId\") REFERENCES \"SavedTeam\" (\"id\") ON DELETE CASCADE ON UPDATE CASCADE\n);\n\n-- CreateTable\nCREATE TABLE \"ImportSnapshot\" (\n    \"id\" TEXT NOT NULL PRIMARY KEY,\n    \"source\" TEXT NOT NULL,\n    \"sha256\" TEXT,\n    \"takenAt\" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP\n);\n\n-- CreateIndex\nCREATE UNIQUE INDEX \"SavedTeamMember_teamId_slot_key\" ON \"SavedTeamMember\"(\"teamId\", \"slot\");\n" },
];
