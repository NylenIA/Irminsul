#!/usr/bin/env node
/**
 * Génère `packages/data-access/src/migrations-bundle.ts` à partir du dossier
 * `packages/data-access/prisma/migrations/`.
 *
 * Pourquoi : le runner de migration au démarrage (instrumentation.ts) doit
 * disposer du SQL des migrations À L'EXÉCUTION, y compris dans le bundle desktop
 * standalone où le dossier `prisma/migrations` n'est PAS copié. On embarque donc
 * le SQL comme constante TS (toujours livrée avec le code).
 *
 * La synchronisation dossier <-> bundle est garantie par
 * `packages/data-access/tests/expected-migrations.test.ts` (échoue si divergence).
 * Régénérer après TOUTE nouvelle migration : `node scripts/gen-migrations-bundle.mjs`.
 */
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(
  decodeURIComponent(new URL(".", import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1"),
  "..",
);
const MIGRATIONS_DIR = path.join(ROOT, "packages", "data-access", "prisma", "migrations");
const OUT = path.join(ROOT, "packages", "data-access", "src", "migrations-bundle.ts");

const names = readdirSync(MIGRATIONS_DIR, { withFileTypes: true })
  .filter((e) => e.isDirectory())
  .map((e) => e.name)
  .sort();

const entries = names.map((name) => {
  const sql = readFileSync(path.join(MIGRATIONS_DIR, name, "migration.sql"), "utf8");
  return `  { name: ${JSON.stringify(name)}, sql: ${JSON.stringify(sql)} },`;
});

const content = `// GÉNÉRÉ par scripts/gen-migrations-bundle.mjs — NE PAS ÉDITER À LA MAIN.
// Miroir embarqué des migrations Prisma (dossier prisma/migrations/), disponible
// à l'exécution y compris dans le bundle desktop. Régénérer après toute migration :
//   node scripts/gen-migrations-bundle.mjs
// La synchro dossier <-> bundle est vérifiée par tests/expected-migrations.test.ts.

export interface BundledMigration {
  readonly name: string;
  readonly sql: string;
}

export const MIGRATIONS_BUNDLE: readonly BundledMigration[] = [
${entries.join("\n")}
];
`;

writeFileSync(OUT, content, "utf8");
console.log(`[gen-migrations-bundle] ${names.length} migration(s) -> ${path.relative(ROOT, OUT)}`);
