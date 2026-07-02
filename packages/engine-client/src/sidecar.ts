/**
 * SidecarEngineClient — même contrat que LocalEngineClient, mais le calcul est exécuté
 * par le VRAI moteur Python via `scripts/engine_stdio.py` (process one-shot borné).
 * Sécurité : shell:false, windowsHide:true, timeout+kill, stdin JSON, stdout JSON strict,
 * stderr borné, aucun secret en argument. En cas d'échec → SidecarError (l'appelant peut
 * basculer sur LocalEngineClient ; la provenance reflète TOUJOURS le moteur réellement utilisé).
 */
import { spawn } from "node:child_process";
import {
  DIRECT_HIT_ASSUMPTIONS,
  type DirectHitInput,
  type DirectHitOutcome,
  type DirectHitResult,
  type EngineClient,
} from "./contract";

export class SidecarError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SidecarError";
  }
}

export interface SidecarOptions {
  pythonPath: string;
  scriptPath: string;
  timeoutMs?: number;
}

interface PythonDirectHit {
  raw_base: number;
  non_crit: number;
  crit: number;
  expected: number;
  defense_multiplier: number;
  resistance_multiplier: number;
  expected_crit_multiplier: number;
}

function toSnakeParams(input: DirectHitInput): Record<string, number> {
  const out: Record<string, number> = { scaling: input.scaling, scaling_stat: input.scalingStat };
  const map: [keyof DirectHitInput, string][] = [
    ["flatBaseDamage", "flat_base_damage"],
    ["damageBonus", "damage_bonus"],
    ["critRate", "crit_rate"],
    ["critDamage", "crit_damage"],
    ["attackerLevel", "attacker_level"],
    ["enemyLevel", "enemy_level"],
    ["enemyResistance", "enemy_resistance"],
    ["defenseReduction", "defense_reduction"],
    ["defenseIgnore", "defense_ignore"],
    ["amplifyingReactionMultiplier", "amplifying_reaction_multiplier"],
    ["reactionBonus", "reaction_bonus"],
    ["vulnerabilityMultiplier", "vulnerability_multiplier"],
  ];
  for (const [camel, snake] of map) {
    const value = input[camel];
    if (typeof value === "number") out[snake] = value;
  }
  return out;
}

export async function runSidecar(
  options: SidecarOptions,
  request: { method: string; params: Record<string, unknown> },
): Promise<Record<string, unknown>> {
  const timeoutMs = options.timeoutMs ?? 10000;
  return new Promise((resolve, reject) => {
    const child = spawn(options.pythonPath, [options.scriptPath], {
      shell: false,
      windowsHide: true,
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      child.kill();
      reject(new SidecarError(`timeout après ${timeoutMs} ms`));
    }, timeoutMs);
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => (stdout += chunk));
    child.stderr.on("data", (chunk: string) => {
      if (stderr.length < 2000) stderr += chunk;
    });
    child.on("error", (error) => {
      clearTimeout(timer);
      reject(new SidecarError(`lancement impossible : ${error.message}`));
    });
    child.on("close", () => {
      clearTimeout(timer);
      try {
        const parsed = JSON.parse(stdout) as { ok: boolean; result?: unknown; error?: string };
        if (!parsed.ok) reject(new SidecarError(parsed.error ?? "erreur moteur"));
        else resolve(parsed.result as Record<string, unknown>);
      } catch {
        reject(new SidecarError(`sortie non-JSON (stderr: ${stderr.slice(0, 300) || "vide"})`));
      }
    });
    child.stdin.end(JSON.stringify(request));
  });
}

export class SidecarEngineClient {
  constructor(private readonly options: SidecarOptions) {}

  async calculateDirectHit(input: DirectHitInput): Promise<DirectHitOutcome> {
    const raw = (await runSidecar(this.options, {
      method: "calculate_direct_hit",
      params: toSnakeParams(input),
    })) as unknown as PythonDirectHit;
    const result: DirectHitResult = {
      rawBase: raw.raw_base,
      nonCrit: raw.non_crit,
      crit: raw.crit,
      expected: raw.expected,
      defenseMultiplier: raw.defense_multiplier,
      resistanceMultiplier: raw.resistance_multiplier,
      expectedCritMultiplier: raw.expected_crit_multiplier,
    };
    return {
      result,
      provenance: {
        engine: "python-sidecar",
        formula: "direct_hit@irminsul-damage",
        registryStatus: "verified",
        assumptions: DIRECT_HIT_ASSUMPTIONS,
      },
    };
  }
}

// NOTE contrat : EngineClient est synchrone (LocalEngineClient) ; le sidecar est async.
// Le repli sidecar→local est géré explicitement par l'appelant serveur (engine-actions),
// et `provenance.engine` reflète toujours le moteur réellement utilisé.
export type { EngineClient };
