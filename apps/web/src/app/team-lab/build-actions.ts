"use server";

import { readFile } from "node:fs/promises";
import path from "node:path";
import { normalizePlayerBuild, type PlayerCharacterBuild } from "@irminsul/engine-client";
import { accountDir } from "@/server/account";

export type PlayerBuildResult =
  | { ok: true; build: PlayerCharacterBuild }
  | { ok: false; reason: "no_scan" | "not_in_scan" };

// Résolution PARTAGÉE (env desktop IRMINSUL_DATA_DIR sinon repo) — cf. @/server/account.
const ACCOUNT_DIR = accountDir();

/**
 * Charge le build RÉEL d'un personnage depuis le scan local (GOOD, gitignoré).
 * Serveur uniquement — seul le DTO du personnage demandé part vers le client.
 * Le nom du roster (genshin-db) est converti en clé GOOD (sans espaces/apostrophes).
 */
export async function loadPlayerBuildAction(characterName: string): Promise<PlayerBuildResult> {
  let charactersRaw: string;
  let profileRaw: string | null = null;
  try {
    charactersRaw = await readFile(path.join(ACCOUNT_DIR, "characters.json"), "utf8");
    profileRaw = await readFile(path.join(ACCOUNT_DIR, "account-profile.json"), "utf8").catch(
      () => null,
    );
  } catch {
    return { ok: false, reason: "no_scan" };
  }
  try {
    const characters = (JSON.parse(charactersRaw)?.characters ?? {}) as Record<string, never>;
    const profile = profileRaw ? JSON.parse(profileRaw) : null;
    const goodKey = characterName.replace(/['’\s-]/g, "");
    const raw = characters[goodKey] ?? characters[characterName as never];
    const build = normalizePlayerBuild(raw, profile);
    if (!build) return { ok: false, reason: "not_in_scan" };
    return { ok: true, build };
  } catch {
    return { ok: false, reason: "no_scan" };
  }
}
