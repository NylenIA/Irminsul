/**
 * Génération d'un SQUELETTE de configuration gcsim depuis une équipe.
 *
 * Honnêteté (règle dps.md + skill genshin-dps) : ce n'est PAS une simulation ni
 * un build réel. C'est un point de départ éditable — clés de personnages en
 * best-effort (à vérifier contre la liste gcsim), armes/artéfacts/stats et
 * rotation laissés en TODO explicites. Rien n'est inventé : aucune stat, aucun
 * DPS, aucune rotation par défaut trompeuse.
 */

export const GCSIM_CONFIG_CONTRACT_VERSION = "gcsim-config/1.0";

export interface GcsimSkeletonMember {
  character: string;
  slot: number;
}

/** Sous-ensemble d'un build réel (scan GOOD) utile à gcsim. Aucune stat substat. */
export interface GcsimBuildInput {
  level?: number;
  ascension?: number;
  constellation?: number;
  talents?: { normal?: number; skill?: number; burst?: number };
  weapon?: { id: string; refinement?: number };
  artifactSets?: { set: string; count: number }[];
}

/** Niveau max d'une phase d'ascension (A0..A6). Défaut 90 hors bornes. */
export function ascensionMaxLevel(ascension: number | undefined): number {
  const caps = [20, 40, 50, 60, 70, 80, 90];
  if (ascension === undefined || ascension < 0 || ascension >= caps.length) return 90;
  return caps[ascension]!;
}

/**
 * Clé gcsim best-effort : minuscule + alphanumérique uniquement. Correspond à
 * la convention gcsim pour beaucoup de personnages, MAIS pas tous (les noms à
 * prénom/patronyme comme « Kamisato Ayaka » → `ayaka` dans gcsim). Chaque ligne
 * générée annote le nom source pour permettre la correction manuelle.
 */
export function normalizeGcsimKey(name: string): string {
  return name
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "") // diacritiques
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");
}

/**
 * Produit un squelette gcsim valide syntaxiquement (header options/target +
 * blocs personnages), prêt à compléter puis lancer. Ne renvoie JAMAIS de config
 * "prête" : les armes/sets/stats/rotation sont des TODO.
 */
export function teamToGcsimSkeleton(
  members: readonly GcsimSkeletonMember[],
  options?: { builds?: Readonly<Record<string, GcsimBuildInput>> },
): string {
  const named = members
    .filter((m) => m.character && m.character.trim().length > 0)
    .slice()
    .sort((a, b) => a.slot - b.slot);

  if (named.length === 0) {
    throw new RangeError("Équipe vide : aucun personnage à convertir en config gcsim.");
  }
  if (named.length > 4) {
    throw new RangeError(`Une équipe Genshin compte au plus 4 personnages ; reçu ${named.length}.`);
  }

  const builds = options?.builds ?? {};
  const keys = named.map((m) => ({ key: normalizeGcsimKey(m.character), name: m.character }));
  const lines: string[] = [
    "// SQUELETTE gcsim genere depuis une equipe Irminsul — PAS une simulation.",
    "// Perso/arme/set pre-remplis depuis ton scan GOOD quand dispo ; sinon TODO.",
    "// Les stats (substats) et la rotation restent A COMPLETER : sans elles, le DPS",
    "// n'est pas representatif. Verifie les cles de personnages (convention gcsim).",
    "",
    "options iteration=1000 duration=90 swap_delay=12;",
    "target lvl=100 resist=0.1 pos=0,0;",
    "",
  ];

  for (const { key, name } of keys) {
    const b = builds[name];
    // Ligne personnage : renseignee depuis le build si dispo, sinon defauts neutres.
    const lvl = b?.level ?? 90;
    const maxLvl = ascensionMaxLevel(b?.ascension);
    const cons = b?.constellation ?? 0;
    const t = b?.talents;
    const talent = `${t?.normal ?? 9},${t?.skill ?? 9},${t?.burst ?? 9}`;
    lines.push(
      `${key} char lvl=${lvl}/${maxLvl} cons=${cons} talent=${talent}; ` +
        `// depuis "${name}" — verifier la cle gcsim`,
    );

    // Arme : cle GOOD->gcsim fiable apres normalisation (ex. NoblesseOblige->noblesseoblige).
    if (b?.weapon?.id) {
      lines.push(
        `${key} add weapon="${normalizeGcsimKey(b.weapon.id)}" refine=${b.weapon.refinement ?? 1} lvl=90/90;`,
      );
    } else {
      lines.push(`${key} add weapon="TODO" refine=1 lvl=90/90;`);
    }

    // Sets d'artefacts.
    if (b?.artifactSets && b.artifactSets.length > 0) {
      for (const s of b.artifactSets) {
        lines.push(`${key} add set="${normalizeGcsimKey(s.set)}" count=${s.count};`);
      }
    } else {
      lines.push(`${key} add set="TODO" count=4;`);
    }

    lines.push(
      `${key} add stats hp=0 atk=0 em=0; // TODO stats substats reelles (non fournies par le scan)`,
    );
    lines.push("");
  }

  lines.push(`active ${keys[0]!.key};`);
  lines.push("// TODO rotation : ex. " + keys.map((k) => `${k.key} skill`).join(", ") + ";");
  lines.push("");
  return lines.join("\n");
}
