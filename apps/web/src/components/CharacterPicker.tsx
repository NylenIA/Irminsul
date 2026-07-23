"use client";

import { Select } from "@irminsul/ui";
import type { CharacterSummary } from "@/lib/roster";

/**
 * Sélecteur de personnage du roster — format unifié « Nom · Élément », option
 * vide explicite, exclusion des personnages déjà pris (le personnage courant
 * reste toujours sélectionnable). Bâti sur la primitive Select (a11y native :
 * l'aria-label est requis). Domaine Genshin → vit côté app, pas dans @irminsul/ui.
 */
export function CharacterPicker({
  roster,
  value,
  onChange,
  ariaLabel,
  excludeNames,
  emptyLabel = "— choisir —",
}: {
  roster: CharacterSummary[];
  value: string;
  onChange: (name: string) => void;
  ariaLabel: string;
  /** Noms à masquer (ex. déjà présents dans un autre emplacement d'équipe). */
  excludeNames?: ReadonlySet<string>;
  emptyLabel?: string;
}): React.ReactElement {
  const options = roster.filter((c) => !excludeNames?.has(c.name) || c.name === value);
  return (
    <Select value={value} onChange={(e) => onChange(e.target.value)} aria-label={ariaLabel}>
      <option value="">{emptyLabel}</option>
      {options.map((c) => (
        <option key={c.id} value={c.name}>
          {c.element ? `${c.name} · ${c.element}` : c.name}
        </option>
      ))}
    </Select>
  );
}
