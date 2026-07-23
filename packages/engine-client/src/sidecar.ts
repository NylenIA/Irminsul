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
  /** Mode source (dev/web) : Python + pont stdio. */
  pythonPath?: string;
  scriptPath?: string;
  /** Mode desktop : binaire moteur GELÉ (dispatcher canonique) appelé directement. */
  frozenExePath?: string;
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
  const frozen = !!options.frozenExePath;
  const program = frozen ? options.frozenExePath! : options.pythonPath;
  const args = frozen ? [] : [options.scriptPath!];
  if (!program) {
    throw new SidecarError("configuration sidecar invalide (ni frozenExePath ni pythonPath)");
  }
  return new Promise((resolve, reject) => {
    const child = spawn(program, args, {
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
    child.on("close", (code) => {
      clearTimeout(timer);
      try {
        const parsed = JSON.parse(stdout) as {
          ok: boolean;
          result?: unknown;
          error?: string | { type?: string; message?: string };
          engine?: string;
        };
        if (!parsed.ok) {
          const msg = typeof parsed.error === "string"
            ? parsed.error
            : parsed.error?.message ?? `erreur moteur (exit ${code})`;
          reject(new SidecarError(msg));
        } else if (typeof parsed.result !== "object" || parsed.result === null) {
          reject(new SidecarError("réponse hors protocole (result absent)"));
        } else if (!frozen && parsed.engine !== "python-sidecar") {
          // Pont stdio : le champ engine est REQUIS (audit). Le binaire gelé (protocole
          // sidecar.py {id,ok,result}) n'émet pas ce champ — sa provenance est vérifiée
          // par engine_provenance (frozen_binary, méthodes, hash).
          reject(new SidecarError(`réponse hors protocole (engine=${parsed.engine ?? "absent"})`));
        } else {
          resolve(parsed.result as Record<string, unknown>);
        }
      } catch {
        reject(new SidecarError(`sortie non-JSON (exit ${code}, stderr: ${stderr.slice(0, 300) || "vide"})`));
      }
    });
    // Le binaire gelé attend {id, method, params} ; le pont stdio ignore id — format unique OK.
    child.stdin.end(JSON.stringify({ id: request.method, ...request }));
  });
}

export class SidecarEngineClient {
  constructor(private readonly options: SidecarOptions) {}

  async calculateDirectHit(input: DirectHitInput): Promise<DirectHitOutcome> {
    const raw = (await runSidecar(this.options, {
      method: "calculate_direct_hit",
      params: toSnakeParams(input),
    })) as unknown as PythonDirectHit;
    // Audit Codex : valider le schéma numérique avant de résoudre (jamais de NaN/undefined
    // étiqueté "python-sidecar").
    const fields: (keyof PythonDirectHit)[] = [
      "raw_base", "non_crit", "crit", "expected",
      "defense_multiplier", "resistance_multiplier", "expected_crit_multiplier",
    ];
    for (const field of fields) {
      if (!Number.isFinite(raw[field])) {
        throw new SidecarError(`champ manquant ou non numérique dans la réponse moteur : ${field}`);
      }
    }
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
