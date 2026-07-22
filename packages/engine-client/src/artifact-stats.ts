/**
 * Somme de la CONTRIBUTION des artéfacts (main + substats) au format gcsim.
 *
 * Rigueur (dps.md) : gcsim `add stats` attend la contribution des artéfacts,
 * PAS les stats finales totales (sinon double-comptage base+arme). Les % sont
 * en DÉCIMAL (46,6 % → 0.466), les plats en valeur brute (ATQ 311 → 311).
 *
 * GOOD ne stocke pas la valeur du main stat, seulement sa clé → table EXACTE
 * des mains 5★ niveau 20 (source : valeurs officielles/KQM). Un artéfact hors
 * 5★-niv20 rend le calcul incomplet (`complete=false`) : l'appelant laisse
 * alors un TODO plutôt qu'une somme fausse. Aucune valeur approximée.
 */

export interface GoodArtifactLike {
  rarity: number;
  level: number;
  mainStatKey: string;
  substats: { key: string; value: number }[];
}

export interface ArtifactStatSum {
  /** Clés gcsim (hp, atk, atk%, em, er, cr, cd, pyro%, …). % en décimal. */
  stats: Record<string, number>;
  /** true seulement si TOUS les artéfacts fournis sont calculables (5★ niv20). */
  complete: boolean;
}

/** GOOD statKey -> [clé gcsim, pourcentage ?]. Couvre mains ET substats. */
const STAT_MAP: Record<string, [string, boolean]> = {
  hp: ["hp", false],
  hp_: ["hp%", true],
  atk: ["atk", false],
  atk_: ["atk%", true],
  def: ["def", false],
  def_: ["def%", true],
  eleMas: ["em", false],
  enerRech_: ["er", true],
  critRate_: ["cr", true],
  critDMG_: ["cd", true],
  heal_: ["heal", true],
  physical_dmg_: ["phys%", true],
  anemo_dmg_: ["anemo%", true],
  geo_dmg_: ["geo%", true],
  electro_dmg_: ["electro%", true],
  hydro_dmg_: ["hydro%", true],
  pyro_dmg_: ["pyro%", true],
  cryo_dmg_: ["cryo%", true],
  dendro_dmg_: ["dendro%", true],
};

/** Valeur EXACTE du main stat d'un artéfact 5★ niveau 20 (format gcsim). */
const MAIN_5STAR_L20: Record<string, number> = {
  hp: 4780,
  atk: 311,
  hp_: 0.466,
  atk_: 0.466,
  def_: 0.583,
  eleMas: 187,
  enerRech_: 0.518,
  critRate_: 0.311,
  critDMG_: 0.622,
  heal_: 0.359,
  physical_dmg_: 0.583,
  anemo_dmg_: 0.466,
  geo_dmg_: 0.466,
  electro_dmg_: 0.466,
  hydro_dmg_: 0.466,
  pyro_dmg_: 0.466,
  cryo_dmg_: 0.466,
  dendro_dmg_: 0.466,
};

function bump(stats: Record<string, number>, gcsimKey: string, value: number): void {
  stats[gcsimKey] = Math.round(((stats[gcsimKey] ?? 0) + value) * 10000) / 10000;
}

/** Ajoute une valeur au format GOOD brut (% divisé par 100). Ignore les clés inconnues. */
function addGoodRaw(stats: Record<string, number>, goodKey: string, rawValue: number): void {
  const entry = STAT_MAP[goodKey];
  if (!entry) return;
  const [gcsimKey, isPercent] = entry;
  bump(stats, gcsimKey, isPercent ? rawValue / 100 : rawValue);
}

export function sumArtifactStats(artifacts: readonly GoodArtifactLike[]): ArtifactStatSum {
  const stats: Record<string, number> = {};
  let complete = artifacts.length > 0;
  for (const art of artifacts) {
    // Gate strict : seule la table 5★ niv20 est exacte. Sinon on n'invente rien.
    if (art.rarity !== 5 || art.level !== 20 || MAIN_5STAR_L20[art.mainStatKey] === undefined) {
      complete = false;
      continue;
    }
    // Main stat : déjà au format gcsim (0.466 ou 4780) → ajout direct.
    const mainEntry = STAT_MAP[art.mainStatKey];
    if (mainEntry) bump(stats, mainEntry[0], MAIN_5STAR_L20[art.mainStatKey]!);
    // Substats : format GOOD brut (9.3 → 0.093 pour un %).
    for (const s of art.substats) {
      if (s && typeof s.value === "number") addGoodRaw(stats, s.key, s.value);
    }
  }
  return { stats, complete };
}
