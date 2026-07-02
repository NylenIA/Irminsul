import { describe, expect, it } from "vitest";
import { existsSync } from "node:fs";
import path from "node:path";
import { LocalEngineClient } from "../src/direct-hit";
import { runSidecar, SidecarEngineClient, SidecarError } from "../src/sidecar";

const ROOT = path.join(process.cwd(), "..", "..");
const PYTHON = path.join(ROOT, ".venv", "Scripts", "python.exe");
const SCRIPT = path.join(ROOT, "scripts", "engine_stdio.py");
const available = existsSync(PYTHON) && existsSync(SCRIPT);

describe.skipIf(!available)("SidecarEngineClient — vrai moteur Python via stdio", () => {
  const options = { pythonPath: PYTHON, scriptPath: SCRIPT, timeoutMs: 15000 };

  it("parité à travers le pont : sidecar == LocalEngineClient (mêmes formules)", async () => {
    const input = {
      scaling: 2.5,
      scalingStat: 2000,
      critRate: 0.6,
      critDamage: 1.2,
      damageBonus: 0.466,
      amplifyingReactionMultiplier: 1.5,
    };
    const viaSidecar = await new SidecarEngineClient(options).calculateDirectHit(input);
    const viaLocal = new LocalEngineClient().calculateDirectHit(input);
    expect(viaSidecar.result.expected).toBeCloseTo(viaLocal.result.expected, 9);
    expect(viaSidecar.result.crit).toBeCloseTo(viaLocal.result.crit, 9);
    expect(viaSidecar.provenance.engine).toBe("python-sidecar");
  });

  it("méthode inconnue → SidecarError typée (pas de sortie brute)", async () => {
    await expect(runSidecar(options, { method: "nope", params: {} })).rejects.toBeInstanceOf(SidecarError);
  });
});

describe("SidecarEngineClient — échec de lancement", () => {
  it("python introuvable → SidecarError (l'appelant bascule sur LocalEngineClient)", async () => {
    const bad = new SidecarEngineClient({
      pythonPath: path.join(ROOT, "nope", "python.exe"),
      scriptPath: SCRIPT,
      timeoutMs: 3000,
    });
    await expect(bad.calculateDirectHit({ scaling: 1, scalingStat: 100 })).rejects.toBeInstanceOf(SidecarError);
  });
});
