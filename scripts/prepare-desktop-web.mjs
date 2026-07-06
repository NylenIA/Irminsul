#!/usr/bin/env node
/**
 * Prépare les ressources desktop Tauri (idempotent, appelé par beforeBuildCommand) :
 * 1. build Next standalone (apps/web) ;
 * 2. copie standalone + .next/static + public → app/src-tauri/web/standalone/... ;
 * 3. embarque le runtime Node (node.exe courant, licence MIT) → binaries/node-<triple>.exe ;
 * 4. génère une base SQLite TEMPLATE pré-migrée (prisma migrate deploy) → web-template.db ;
 * 5. écrit les hashes dans .irminsul/proof/desktop-resources.json.
 * Résolution uniforme dev/prod : tout est résolu via resource_dir Tauri.
 */
import { execSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, rmSync, writeFileSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import process from "node:process";

const ROOT = path.resolve(decodeURIComponent(new URL(".", import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1"), "..");
const TAURI = path.join(ROOT, "app", "src-tauri");
const WEB = path.join(ROOT, "apps", "web");
const OUT = path.join(TAURI, "web", "standalone");
const NODE_DEST = path.join(TAURI, "binaries", "node-x86_64-pc-windows-msvc.exe");
const TEMPLATE_DB = path.join(TAURI, "web-template.db");

const sha256 = (p) => createHash("sha256").update(readFileSync(p)).digest("hex");
const run = (cmd, cwd = ROOT) => { console.log(`[prepare] ${cmd}`); execSync(cmd, { cwd, stdio: "inherit" }); };

// 1) Build Next standalone.
run("npm run build -w @irminsul/web");

// 2) Ressources web (structure standalone attendue par server.js).
rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync(path.join(WEB, ".next", "standalone"), OUT, { recursive: true });
cpSync(path.join(WEB, ".next", "static"), path.join(OUT, "apps", "web", ".next", "static"), { recursive: true });
if (existsSync(path.join(WEB, "public"))) {
  cpSync(path.join(WEB, "public"), path.join(OUT, "apps", "web", "public"), { recursive: true });
}

// 3) Runtime Node embarqué (auto-suffisant : pas de Node global requis à l'exécution).
mkdirSync(path.dirname(NODE_DEST), { recursive: true });
cpSync(process.execPath, NODE_DEST);

// 4) Base template pré-migrée (le CLI prisma n'est PAS embarqué : migration au BUILD,
//    premier lancement = simple copie du template vers le dossier utilisateur).
rmSync(TEMPLATE_DB, { force: true });
console.log("[prepare] prisma migrate deploy -> web-template.db");
execSync(`npx prisma migrate deploy --schema prisma/schema.prisma`, {
  cwd: path.join(ROOT, "packages", "data-access"), // prisma CLI = devDep du workspace data-access
  stdio: "inherit",
  env: { ...process.env, DATABASE_URL: `file:${TEMPLATE_DB.replace(/\\/g, "/")}` },
});

// 5) Preuves.
const proof = {
  preparedAt: new Date().toISOString(),
  node: { version: process.version, arch: process.arch, license: "MIT (Node.js)", from: process.execPath, sha256: sha256(NODE_DEST), sizeBytes: statSync(NODE_DEST).size },
  serverJs: { path: "web/standalone/apps/web/server.js", exists: existsSync(path.join(OUT, "apps", "web", "server.js")) },
  templateDb: { path: "web-template.db", sha256: existsSync(TEMPLATE_DB) ? sha256(TEMPLATE_DB) : null },
};
mkdirSync(path.join(ROOT, ".irminsul", "proof"), { recursive: true });
writeFileSync(path.join(ROOT, ".irminsul", "proof", "desktop-resources.json"), JSON.stringify(proof, null, 2));
console.log(`[prepare] OK node=${process.version} serverJs=${proof.serverJs.exists} templateDb=${!!proof.templateDb.sha256}`);
if (!proof.serverJs.exists || !proof.templateDb.sha256) process.exit(1);
