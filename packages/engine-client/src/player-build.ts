/**
 * Adapter builds du compte (scan AkashaScanner/InventoryKamera au format GOOD).
 * Normalisation PURE (les E/S fichier restent côté serveur applicatif).
 * Règle : AUCUNE stat inventée — on expose ce que le scan contient, avec provenance,
 * et on liste explicitement ce qui manque (ex. stats finales, non dérivables ici).
 */

export interface PlayerCharacterBuild {
  characterId: string;
  level?: number;
  ascension?: number;
  constellation?: number;
  talents?: { normal?: number; skill?: number; burst?: number };
  weapon?: { id: string; refinement?: number };
  artifactSlots?: string[];
  source: "scanner" | "local-db" | "manual" | "fixture";
  scannerName?: string;
  importedAt?: string;
  confidence: "high" | "medium" | "low";
  /** Ce que ce build NE contient PAS (affiché tel quel, jamais estimé). */
  missing: string[];
}

interface RawGoodCharacter {
  key?: string;
  level?: number;
  ascension?: number;
  constellation?: number;
  talents?: { auto?: number; skill?: number; burst?: number };
  weapon?: string;
  artifacts?: Record<string, string>;
}

interface RawProfile {
  snapshot_date?: string;
  source?: string;
  format?: string;
}

/** `w-008-WolfsGravestone-r1-055aea9d` → { id: "WolfsGravestone", refinement: 1 } */
export function parseWeaponRef(ref: string | undefined): PlayerCharacterBuild["weapon"] {
  if (!ref) return undefined;
  const match = /^w-\d+-(.+?)-r(\d+)-[0-9a-f]+$/i.exec(ref);
  if (!match) return { id: ref };
  return { id: match[1] as string, refinement: Number(match[2]) };
}

export function normalizePlayerBuild(
  raw: RawGoodCharacter | undefined,
  profile: RawProfile | null,
): PlayerCharacterBuild | null {
  if (!raw?.key) return null;
  const missing: string[] = [];
  if (raw.level === undefined) missing.push("niveau");
  if (raw.talents === undefined) missing.push("talents");
  if (raw.weapon === undefined) missing.push("arme");
  // Toujours vrai sur cette branche : les stats finales exigent le moteur phase3 (basestats
  // + weaponstats + artéfacts résolus). On ne les estime JAMAIS.
  missing.push("stats finales (saisie manuelle requise — calcul phase3 non fusionné)");

  return {
    characterId: raw.key,
    level: raw.level,
    ascension: raw.ascension,
    constellation: raw.constellation,
    talents: raw.talents
      ? { normal: raw.talents.auto, skill: raw.talents.skill, burst: raw.talents.burst }
      : undefined,
    weapon: parseWeaponRef(raw.weapon),
    artifactSlots: raw.artifacts ? Object.keys(raw.artifacts) : undefined,
    source: "scanner",
    scannerName: profile?.source,
    importedAt: profile?.snapshot_date,
    // GOOD scanné par outil connu, non altéré manuellement → confiance haute sur CE contenu.
    confidence: profile?.format === "GOOD" ? "high" : "medium",
    missing,
  };
}
