import charactersData from "./characters.json";

/** Contrat stable de personnage (adapter isolé). Données réelles uniquement. */
export interface CharacterSummary {
  id: string;
  name: string;
  element: string | null;
  rarity: number | null;
  weapon: string | null;
  source: "scanner" | "local-data" | "engine" | "fixture";
}

/** Roster réel issu de la source LOCALE genshin-db (généré par scripts/gen-web-roster.py).
 *  Aucune donnée inventée. À terme, fusionné/écrasé par le scan de compte (source: 'scanner'). */
export const CHARACTERS: CharacterSummary[] = charactersData as unknown as CharacterSummary[];

export const ROSTER_SOURCE_LABEL = "Données locales (genshin-db)";
