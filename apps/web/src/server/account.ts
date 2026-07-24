/**
 * Lecture SERVEUR du scan de compte local (GOOD, gitignoré — données personnelles).
 * Jamais importé côté client : seules les données normalisées partent au rendu.
 */
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { normalizePlayerBuild, type PlayerCharacterBuild } from "@irminsul/engine-client";

/**
 * Racine des données : `IRMINSUL_DATA_DIR` (posée par Tauri en desktop —
 * %APPDATA%/com.nylenia.irminsul) sinon `<repo>/data` (dev). Même logique que
 * `src/irminsul/paths.py` côté moteur : app et sidecar lisent le MÊME dossier.
 */
export function dataRoot(): string {
  return process.env["IRMINSUL_DATA_DIR"] ?? path.join(process.cwd(), "..", "..", "data");
}

/**
 * Dossier du compte courant.
 *
 * Emplacement CANONIQUE : `<dataRoot>/account/current`.
 *
 * Repli HISTORIQUE : d'anciennes versions desktop écrivaient sous
 * `<dataRoot>/data/account/current` (un niveau `data/` en trop). Un compte
 * importé avec ces versions devenait INVISIBLE après mise à jour — l'app
 * affichait « aucun scan » alors que les données existaient. On lit donc
 * l'ancien emplacement s'il est le seul present, au lieu de perdre le compte.
 */
export function accountDir(): string {
  const canonical = path.join(dataRoot(), "account", "current");
  if (existsSync(canonical)) return canonical;
  const legacy = path.join(dataRoot(), "data", "account", "current");
  if (existsSync(legacy)) return legacy;
  return canonical;
}

export interface AccountSummary {
  scannerName?: string;
  importedAt?: string;
  format?: string;
  characters: PlayerCharacterBuild[];
}

export async function loadAccountSummary(): Promise<AccountSummary | null> {
  let charactersRaw: string;
  let profile: { snapshot_date?: string; source?: string; format?: string } | null = null;
  try {
    charactersRaw = await readFile(path.join(accountDir(), "characters.json"), "utf8");
    profile = JSON.parse(
      await readFile(path.join(accountDir(), "account-profile.json"), "utf8"),
    );
  } catch {
    return null; // pas de scan local : l'UI affiche l'état vide honnête
  }
  try {
    const parsed = JSON.parse(charactersRaw) as { characters?: Record<string, never> };
    const characters = Object.values(parsed.characters ?? {})
      .map((raw) => normalizePlayerBuild(raw, profile))
      .filter((b): b is PlayerCharacterBuild => b !== null)
      .sort((a, b) => (b.level ?? 0) - (a.level ?? 0) || a.characterId.localeCompare(b.characterId));
    return {
      scannerName: profile?.source,
      importedAt: profile?.snapshot_date,
      format: profile?.format,
      characters,
    };
  } catch {
    return null;
  }
}
