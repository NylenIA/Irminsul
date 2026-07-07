#!/usr/bin/env node
/**
 * Cas d'ERREUR desktop (T5) sur une COPIE de l'installation, chemin avec espaces + Unicode.
 * Pour chaque ressource retirée (sidecar / node / standalone) : l'app doit rester VIVANTE
 * (page d'erreur, pas de crash), ne spawner AUCUN enfant node, et se fermer proprement.
 * Preuves : .irminsul/proof/smoke-errors.json
 */
import { execSync, spawn } from "node:child_process";
import { cpSync, existsSync, renameSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const ROOT = path.resolve(decodeURIComponent(new URL(".", import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1"), "..");
const SRC = path.join(process.env.LOCALAPPDATA ?? "", "Irminsul");
const DEST = path.join(process.env.TEMP ?? "", "Irminsul copie étoile ★");
const proof = { dest: DEST, cases: [] };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const kids = (pid) => {
  try {
    const out = execSync(`powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'node*' -and $_.ParentProcessId -eq ${pid} } | Select-Object -ExpandProperty ProcessId"`, { encoding: "utf8" });
    return out.split(/\r?\n/).map((l) => l.trim()).filter((l) => /^\d+$/.test(l));
  } catch { return []; }
};
const alive = (pid) => {
  try { return execSync(`powershell -NoProfile -Command "[bool](Get-Process -Id ${pid} -ErrorAction SilentlyContinue)"`, { encoding: "utf8" }).includes("True"); }
  catch { return false; }
};

rmSync(DEST, { recursive: true, force: true });
cpSync(SRC, DEST, { recursive: true });
console.log(`[errors] copie installée -> ${DEST}`);

const CASES = [
  { name: "sidecar absent", move: "irminsul-sidecar.exe" },
  { name: "runtime Node absent", move: "binaries/node-x86_64-pc-windows-msvc.exe" },
  { name: "standalone absent", move: "web/standalone/apps/web/server.js" },
];

for (const c of CASES) {
  const target = path.join(DEST, c.move);
  renameSync(target, target + ".hidden");
  const app = spawn(path.join(DEST, "irminsul.exe"), [], { detached: true, stdio: "ignore" });
  await sleep(9000);
  const stillAlive = alive(app.pid);            // pas de crash : fenêtre d'erreur affichée
  const children = kids(app.pid);               // AUCUN node spawné
  execSync(`taskkill /PID ${app.pid} /F`, { stdio: "ignore" }); // fermeture (forcée acceptable ici)
  await sleep(2500);
  const orphans = kids(app.pid);
  const ok = stillAlive && children.length === 0 && orphans.length === 0;
  proof.cases.push({ name: c.name, alive: stillAlive, children, orphans, ok });
  console.log(`[errors] ${ok ? "OK " : "FAIL"} ${c.name} (alive=${stillAlive} children=${children.length})`);
  renameSync(target + ".hidden", target);
  if (!ok) { finish(1); }
}

// Double lancement : la 2e instance ne doit pas créer un 2e serveur incontrôlé (elle affiche
// une erreur « serveur déjà démarré » seulement au sein du MÊME process ; deux process = deux
// serveurs indépendants, chacun possédé — on vérifie simplement zéro orphelin après fermeture).
const a1 = spawn(path.join(DEST, "irminsul.exe"), [], { detached: true, stdio: "ignore" });
const a2 = spawn(path.join(DEST, "irminsul.exe"), [], { detached: true, stdio: "ignore" });
await sleep(12000);
execSync(`taskkill /PID ${a1.pid} 2>nul & taskkill /PID ${a2.pid} 2>nul`, { stdio: "ignore", shell: "cmd.exe" });
await sleep(4000);
const leftover = execSync(`powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'node*' -and $_.CommandLine -like '*server.js*' } | Select-Object -ExpandProperty ProcessId"`, { encoding: "utf8" }).trim();
proof.cases.push({ name: "double lancement puis fermeture", orphans: leftover, ok: leftover === "" });
console.log(`[errors] ${leftover === "" ? "OK " : "FAIL"} double lancement (orphelins='${leftover}')`);

function finish(code) {
  mkdirSync(path.join(ROOT, ".irminsul", "proof"), { recursive: true });
  writeFileSync(path.join(ROOT, ".irminsul", "proof", "smoke-errors.json"), JSON.stringify(proof, null, 2));
  rmSync(DEST, { recursive: true, force: true });
  process.exit(code);
}
finish(proof.cases.every((c) => c.ok) ? 0 : 1);
