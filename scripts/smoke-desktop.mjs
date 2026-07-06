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
import { existsSync, readFileSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const ROOT = path.resolve(decodeURIComponent(new URL(".", import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1"), "..");
const EXE = process.argv[2] ?? path.join(ROOT, "app", "src-tauri", "target", "release", "irminsul.exe");
const APPDATA_DIR = path.join(process.env.APPDATA ?? "", "com.nylenia.irminsul");
const LOG = path.join(APPDATA_DIR, "logs", "next-server.log");
const ROUTES = ["/", "/team-lab", "/rotations", "/team-compare", "/recommendations", "/import-export"];
const proof = { exe: EXE, startedAt: new Date().toISOString(), steps: [] };
const step = (name, ok, detail = "") => { proof.steps.push({ name, ok, detail }); console.log(`[smoke] ${ok ? "OK " : "FAIL"} ${name} ${detail}`); if (!ok) finish(1); };
function finish(code) {
  mkdirSync(path.join(ROOT, ".irminsul", "proof"), { recursive: true });
  writeFileSync(path.join(ROOT, ".irminsul", "proof", "smoke-desktop.json"), JSON.stringify(proof, null, 2));
  process.exit(code);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const nodePids = () => {
  // wmic est absent des Windows 11 récents → CIM via PowerShell.
  try {
    const out = execSync(
      `powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'node*' -and $_.CommandLine -like '*server.js*' } | Select-Object -ExpandProperty ProcessId"`,
      { encoding: "utf8" },
    );
    return out.split(/\r?\n/).map((l) => l.trim()).filter((l) => /^\d+$/.test(l));
  } catch { return []; }
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

// 2) Readiness : port réel depuis le log Next (borné 60 s).
let port = null;
for (let i = 0; i < 120 && !port; i++) {
  await sleep(500);
  if (existsSync(LOG)) {
    const m = readFileSync(LOG, "utf8").match(/127\.0\.0\.1:(\d+)/);
    if (m) port = Number(m[1]);
  }
}
step("readiness (port du log Next)", !!port, `port=${port}`);
proof.port = port;
proof.nodePids = nodePids();
step("processus Node enfant présent", proof.nodePids.length > 0, `pids=${proof.nodePids}`);

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

// 6) Relance → persistance (la DB existe toujours, le serveur redémarre).
rmSync(LOG, { force: true });
const app2 = spawn(EXE, [], { detached: true, stdio: "ignore" });
let port2 = null;
for (let i = 0; i < 120 && !port2; i++) {
  await sleep(500);
  if (existsSync(LOG)) { const m = readFileSync(LOG, "utf8").match(/127\.0\.0\.1:(\d+)/); if (m) port2 = Number(m[1]); }
}
step("relance + readiness", !!port2, `port=${port2}`);
step("persistance DB", existsSync(path.join(APPDATA_DIR, "irminsul.db")), `dbExistaitAvant=${dbExisted}`);
execSync(`taskkill /PID ${app2.pid}`, { stdio: "ignore" });
await sleep(4000);
step("aucun orphelin après 2e fermeture", nodePids().length === 0, "");

proof.finishedAt = new Date().toISOString();
console.log("[smoke] TOUT VERT");
finish(0);
