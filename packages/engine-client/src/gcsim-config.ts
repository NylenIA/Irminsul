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
export function teamToGcsimSkeleton(members: readonly GcsimSkeletonMember[]): string {
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

  const keys = named.map((m) => ({ key: normalizeGcsimKey(m.character), name: m.character }));
  const lines: string[] = [
    "// SQUELETTE gcsim genere depuis une equipe Irminsul — PAS une simulation.",
    "// A completer : cles a verifier (liste gcsim), armes/sets/stats et rotation.",
    "// Tant que les TODO ne sont pas remplis, le resultat n'a aucune valeur.",
    "",
    "options iteration=1000 duration=90 swap_delay=12;",
    "target lvl=100 resist=0.1 pos=0,0;",
    "",
  ];

  for (const { key, name } of keys) {
    lines.push(`${key} char lvl=90/90 cons=0 talent=9,9,9; // depuis "${name}" — verifier la cle gcsim`);
    lines.push(`${key} add weapon="TODO" refine=1 lvl=90/90;`);
    lines.push(`${key} add set="TODO" count=4;`);
    lines.push(`${key} add stats hp=0 atk=0 em=0; // TODO stats reelles (sinon DPS non representatif)`);
    lines.push("");
  }

  lines.push(`active ${keys[0]!.key};`);
  lines.push("// TODO rotation : ex. " + keys.map((k) => `${k.key} skill`).join(", ") + ";");
  lines.push("");
  return lines.join("\n");
}
