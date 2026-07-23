// Migrations Prisma attendues par CETTE version de l'application.
// Source de vérité : le dossier `prisma/migrations/`. Cette liste en est le miroir
// embarqué (toujours disponible à l'exécution, y compris dans le bundle desktop où
// le dossier `prisma/migrations` n'est pas copié). La synchronisation dossier <-> liste
// est garantie par `tests/expected-migrations.test.ts` (échoue à la moindre divergence).
export const EXPECTED_MIGRATIONS: readonly string[] = [
  "20260630045245_init_local_app_data",
];
