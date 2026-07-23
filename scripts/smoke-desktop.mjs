#!/usr/bin/env node
/**
 * SMOKE TEST du binaire desktop de PRODUCTION (pas `tauri dev`).
 * 1. lance target/release/irminsul.exe ; 2. lit le port réel dans le log Next ;
 * 3. vérifie les routes critiques (HTTP 200 + marqueur Next moderne) ; 4. provenance moteur ;
 * 5. fermeture propre (WM_CLOSE via taskkill sans /F) ; 6. ÉCHOUE si un enfant survit ;
 * 7. relance → persistance DB. Preuves : .irminsul/proof/smoke-desktop.json
 * Usage : node scripts/smoke-desktop.mjs [cheminExeOptionnel]
 */
import { execSync, spawn } from "node:child_process";
import { existsSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const ROOT = path.resolve(decodeURIComponent(new URL(".", import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1"), "..");
const EXE = process.argv[2] ?? path.join(ROOT, "app", "src-tauri", "target", "release", "irminsul.exe");
const APPDATA_DIR = path.join(process.env.APPDATA ?? "", "com.nylenia.irminsul");
const LOG = path.join(APPDATA_DIR, "logs", "next-server.log");
const ROUTES = ["/", "/team-lab", "/rotations", "/team-compare", "/recommendations", "/import-export", "/diagnostic"];
const proof = { exe: EXE, startedAt: new Date().toISOString(), steps: [] };
const step = (name, ok, detail = "") => { proof.steps.push({ name, ok, detail }); console.log(`[smoke] ${ok ? "OK " : "FAIL"} ${name} ${detail}`); if (!ok) finish(1); };
function finish(code) {
  mkdirSync(path.join(ROOT, ".irminsul", "proof"), { recursive: true });
  writeFileSync(path.join(ROOT, ".irminsul", "proof", "smoke-desktop.json"), JSON.stringify(proof, null, 2));
  process.exit(code);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// LIAISON STRICTE (audit L4) : seuls les node ENFANTS du PID Tauri de CETTE instance comptent.
const nodePidsOf = (parentPid) => {
  try {
    const out = execSync(
      `powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'node*' -and $_.ParentProcessId -eq ${parentPid} } | Select-Object -ExpandProperty ProcessId"`,
      { encoding: "utf8" },
    );
    return out.split(/\r?\n/).map((l) => l.trim()).filter((l) => /^\d+$/.test(l));
  } catch { return []; }
};
// Node orphelins server.js (peu importe le parent) — pour l'assertion « zéro orphelin ».
const nodePids = () => {
  try {
    const out = execSync(
      `powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'node*' -and $_.CommandLine -like '*server.js*' } | Select-Object -ExpandProperty ProcessId"`,
      { encoding: "utf8" },
    );
    return out.split(/\r?\n/).map((l) => l.trim()).filter((l) => /^\d+$/.test(l));
  } catch { return []; }
};
// Port loopback en LISTEN appartenant au PID donné (lien strict port↔instance, pas de log).
const portOf = (pid) => {
  try {
    const out = execSync(
      `powershell -NoProfile -Command "Get-NetTCPConnection -State Listen -OwningProcess ${pid} -ErrorAction SilentlyContinue | Where-Object { $_.LocalAddress -eq '127.0.0.1' } | Select-Object -ExpandProperty LocalPort"`,
      { encoding: "utf8" },
    );
    const m = out.match(/\d+/);
    return m ? Number(m[0]) : null;
  } catch { return null; }
};

if (!existsSync(EXE)) { step("binaire production présent", false, EXE); }
step("binaire production présent", true, EXE);

// Base propre pour tester le premier lancement ? NON destructif : on note seulement l'état.
const dbExisted = existsSync(path.join(APPDATA_DIR, "irminsul.db"));
rmSync(LOG, { force: true });

// 1) Lancement production.
const app = spawn(EXE, [], { detached: true, stdio: "ignore" });
proof.tauriPid = app.pid;
step("lancement (PID)", !!app.pid, `pid=${app.pid}`);

// 2) Readiness LIÉE À L'INSTANCE (audit L4) : node enfant du PID Tauri, puis port de CE node
// via la table TCP (plus aucun parsing de log — un log périmé ne peut plus fausser le test).
let nodePid = null;
let port = null;
for (let i = 0; i < 120 && !port; i++) {
  await sleep(500);
  if (!nodePid) {
    const kids = nodePidsOf(app.pid);
    if (kids.length > 0) nodePid = kids[0];
  }
  if (nodePid) port = portOf(nodePid);
}
step("node ENFANT de cette instance Tauri", !!nodePid, `tauri=${app.pid} node=${nodePid}`);
step("readiness (port LISTEN de ce node)", !!port, `port=${port}`);
proof.port = port;
proof.nodePids = [nodePid];

// 3) Routes critiques : le frontend MODERNE (marqueurs Next + Archive astrale).
for (const r of ROUTES) {
  const res = await fetch(`http://127.0.0.1:${port}${r}`).catch(() => null);
  const body = res ? await res.text() : "";
  const modern = body.includes("/_next/") || body.includes("Irminsul");
  step(`route ${r}`, !!res && res.status === 200 && modern, `status=${res?.status}`);
}
// Ancien Vite absent : le HTML ne référence PAS les assets Vite.
const home = await (await fetch(`http://127.0.0.1:${port}/`)).text();
step("frontend = Next moderne (pas Vite)", home.includes("/_next/") && !home.includes("vite"), "");

// 3b) Diagnostic : la page expose la provenance du moteur GELÉ (mode desktop).
{
  const diag = await (await fetch(`http://127.0.0.1:${port}/diagnostic`)).text();
  step("diagnostic = mode desktop + moteur gelé", diag.includes("mode desktop") && diag.includes("engine-ipc/1.0"), "");
  // Audit L3 : username dérivé de l'environnement (pas de valeur en dur).
  const userName = path.basename(process.env.USERPROFILE ?? "");
  step("diagnostic sanitizé (pas de nom de compte)", !!userName && !diag.includes(userName), `user=${userName.length} chars`);
}

// 3c) Nonce (audit M3) : une MUTATION sans cookie nonce est REFUSÉE ; les GET restent libres.
{
  const post = await fetch(`http://127.0.0.1:${port}/`, { method: "POST", body: "x" }).catch(() => null);
  step("nonce : POST sans cookie → 403", post?.status === 403, `status=${post?.status}`);
  // Audit L3 : cookie INVALIDE (pas seulement absent) → 403 aussi.
  const postBad = await fetch(`http://127.0.0.1:${port}/`, {
    method: "POST", body: "x", headers: { cookie: "irm_nonce=deadbeef".padEnd(75, "0") },
  }).catch(() => null);
  step("nonce : POST avec cookie invalide → 403", postBad?.status === 403, `status=${postBad?.status}`);
  const boot = await fetch(`http://127.0.0.1:${port}/boot?n=mauvais-nonce`, { redirect: "manual" }).catch(() => null);
  step("nonce : /boot avec nonce invalide → 403", boot?.status === 403, `status=${boot?.status}`);
  // NOTE (documentée) : le round-trip /boot VALIDE n'est pas testable de l'extérieur — le nonce
  // vit uniquement en mémoire (env du serveur + WebView). C'est voulu par le modèle de menace.
}

// 4) Provenance moteur : le sidecar canonique répond depuis le bundle.
try {
  const sidecar = path.join(path.dirname(EXE), "irminsul-sidecar.exe");
  const out = execSync(`"${sidecar}"`, { input: JSON.stringify({ method: "engine_provenance" }), encoding: "utf8", timeout: 60000 });
  const prov = JSON.parse(out);
  step("provenance sidecar (frozen + rotation)", prov.ok === true && prov.result.frozen_binary === true && prov.result.methods.includes("calculate_rotation"), `commit=${prov.result?.git_commit}`);
  proof.engineProvenance = prov.result;
} catch (e) { step("provenance sidecar", false, String(e).slice(0, 120)); }

// 5) Fermeture PROPRE (WM_CLOSE — pas /F : RunEvent::Exit doit tuer l'enfant Node).
execSync(`taskkill /PID ${app.pid}`, { stdio: "ignore" });
await sleep(4000);
const survivors = nodePids();
step("aucun processus Node orphelin après fermeture", survivors.length === 0, `survivants=${survivors}`);

// 6) Relance → persistance (liaison stricte identique).
const app2 = spawn(EXE, [], { detached: true, stdio: "ignore" });
let nodePid2 = null;
let port2 = null;
for (let i = 0; i < 120 && !port2; i++) {
  await sleep(500);
  if (!nodePid2) { const kids = nodePidsOf(app2.pid); if (kids.length > 0) nodePid2 = kids[0]; }
  if (nodePid2) port2 = portOf(nodePid2);
}
step("relance + readiness (node lié)", !!port2, `tauri=${app2.pid} node=${nodePid2} port=${port2}`);
step("persistance DB", existsSync(path.join(APPDATA_DIR, "irminsul.db")), `dbExistaitAvant=${dbExisted}`);
execSync(`taskkill /PID ${app2.pid}`, { stdio: "ignore" });
await sleep(4000);
step("aucun orphelin après 2e fermeture", nodePids().length === 0, "");

proof.finishedAt = new Date().toISOString();
console.log("[smoke] TOUT VERT");
finish(0);
