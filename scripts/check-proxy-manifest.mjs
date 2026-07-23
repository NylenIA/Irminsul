#!/usr/bin/env node
/**
 * Garde anti-régression proxy/nonce (audit PN-01/PN-02) : après `next build`,
 * vérifie dans le manifest Next que le proxy (apps/web/src/proxy.ts) est bien
 * compilé, en runtime nodejs (lecture de IRMINSUL_NONCE via process.env), avec
 * le matcher original intact. Si Next change de convention (upgrade) ou si le
 * fichier proxy n'est plus reconnu, ce gate échoue au lieu d'un arrêt SILENCIEUX
 * de la protection nonce (le 403 runtime desktop reste prouvé par smoke-desktop.mjs).
 * Usage : node scripts/check-proxy-manifest.mjs   (après npm run build)
 */
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(decodeURIComponent(new URL(".", import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1"), "..");
const MANIFEST = path.join(ROOT, "apps", "web", ".next", "server", "functions-config-manifest.json");
const EXPECTED_MATCHER = "/((?!_next/static|_next/image|favicon.ico).*)";

const fail = (msg) => { console.error(`[proxy-manifest] FAIL ${msg}`); process.exit(1); };
const ok = (msg) => console.log(`[proxy-manifest] OK  ${msg}`);

if (!existsSync(MANIFEST)) fail(`manifest absent : ${MANIFEST} — lancer npm run build d'abord`);
const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));

const fn = manifest.functions?.["/_middleware"];
if (!fn) fail(`functions["/_middleware"] absent du manifest — le proxy n'est PLUS reconnu par Next (protection nonce silencieusement inactive ?)`);
ok(`proxy compilé (functions["/_middleware"] présent)`);

if (fn.runtime !== "nodejs") fail(`runtime=${JSON.stringify(fn.runtime)} attendu "nodejs" — lecture process.env IRMINSUL_NONCE non garantie`);
ok(`runtime nodejs`);

const sources = (fn.matchers ?? []).map((m) => m.originalSource);
if (!sources.includes(EXPECTED_MATCHER)) fail(`matcher originalSource=${JSON.stringify(sources)} attendu ${JSON.stringify(EXPECTED_MATCHER)}`);
ok(`matcher original intact`);

console.log("[proxy-manifest] TOUT VERT");
