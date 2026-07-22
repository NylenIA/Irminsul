/**
 * Conversion d'une rotation Irminsul (actions typées) en séquence d'ACTIONS gcsim.
 *
 * Honnêteté (dps.md / skill genshin-rotation) : on exporte l'ORDRE des actions,
 * regroupées par personnage actif. Le timing précis, l'énergie, les cancels et
 * les temps d'attente ne sont PAS modélisés — l'utilisateur doit affiner. Ce
 * n'est pas une rotation optimale ni une garantie de faisabilité en jeu.
 */
import { normalizeGcsimKey } from "./gcsim-config";

export interface RotationActionLike {
  actorId: string;
  kind: string;
}

/** Verbe gcsim par type d'action Irminsul. `swap`/`wait` ne sont pas des verbes. */
const VERB: Record<string, string> = {
  normal_attack: "attack",
  charged_attack: "charge",
  plunging_attack: "high_plunge",
  skill: "skill",
  burst: "burst",
};

/**
 * Retourne des lignes gcsim `active <char>;` + `<char> verbe, verbe;`.
 * `swap` change juste le personnage actif ; `wait` est ignoré (signalé en tête).
 */
export function rotationToGcsimActions(actions: readonly RotationActionLike[]): string {
  const seq: { key: string; verb: string }[] = [];
  let sawWait = false;
  let firstActor: string | null = null;

  for (const a of actions) {
    if (!a.actorId || a.actorId.trim().length === 0) continue;
    const key = normalizeGcsimKey(a.actorId);
    if (firstActor === null) firstActor = key;
    if (a.kind === "wait") {
      sawWait = true;
      continue;
    }
    if (a.kind === "swap") {
      // Le swap fixe le prochain acteur actif ; sans verbe propre en gcsim.
      firstActor = firstActor ?? key;
      seq.push({ key, verb: "" });
      continue;
    }
    const verb = VERB[a.kind];
    if (!verb) continue; // type inconnu : ignoré plutôt qu'invente
    seq.push({ key, verb });
  }

  const withVerb = seq.filter((s) => s.verb.length > 0);
  if (withVerb.length === 0) {
    throw new RangeError("Aucune action exportable (attaque/compétence/déchaînement) dans la rotation.");
  }

  // Groupage des actions contiguës du même personnage en une ligne.
  const lines: string[] = [
    "// Actions gcsim depuis ta rotation Team Lab — ORDRE des actions seulement.",
    "// Timing, energie, cancels" + (sawWait ? " et temps d'attente" : "") + " NON modelises : a affiner.",
    `active ${withVerb[0]!.key};`,
  ];
  let curKey = "";
  let verbs: string[] = [];
  const flush = (): void => {
    if (curKey && verbs.length > 0) lines.push(`${curKey} ${verbs.join(", ")};`);
    verbs = [];
  };
  for (const { key, verb } of withVerb) {
    if (key !== curKey) {
      flush();
      curKey = key;
    }
    verbs.push(verb);
  }
  flush();
  return lines.join("\n") + "\n";
}
