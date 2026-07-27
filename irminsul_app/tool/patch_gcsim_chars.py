"""Installe nos personnages maison dans une copie des sources de gcsim.

Les persos que la communauté n'a pas encore codés (Sandrone, Zibai, …) vivent
dans `tool/gcsim_char/<clé>/`. Ce script les copie dans l'arbre gcsim et les
déclare dans les quatre registres générés, en gardant l'ordre alphabétique.

    python tool/patch_gcsim_chars.py <chemin-vers-gcsim> [clé ...]

GARDE-FOU : si la communauté publie le perso (dossier
`internal/characters/<clé>` déjà présent), on ne touche à rien — leur version
gagne toujours.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
CHARS = TOOL / "gcsim_char"


def insert_sorted_triple(keys_file: Path, key: str, pretty: str) -> None:
    """Insère la clé dans les 3 listes ALIGNÉES de character.dm.go."""
    text = keys_file.read_text(encoding="utf-8")
    if f'"{key}"' in text:
        print(f"  keys: {key} déjà présent")
        return
    names = re.findall(r'^\t"([a-z0-9]+)",$', text, re.M)
    anchor = next((n for n in names if n > key), None)
    if anchor is None:
        raise SystemExit(f"keys: pas d'ancre pour {key}")
    m = re.search(rf"^\t(\w+)\s+// {anchor}$", text, re.M)
    if not m:
        raise SystemExit(f"keys: const de l'ancre {anchor} introuvable")
    ident = m.group(1)
    text = re.sub(rf"(^\t{ident}\s+// {anchor}$)",
                  f"\t{pretty}                        // {key}\n\\1",
                  text, count=1, flags=re.M)
    text = re.sub(rf'(^\t"{anchor}",$)', f'\t"{key}",\n\\1',
                  text, count=1, flags=re.M)
    text = re.sub(rf"(^\t{ident},$)", f"\t{pretty},\n\\1",
                  text, count=1, flags=re.M)
    keys_file.write_text(text, encoding="utf-8")
    print(f"  keys: {key} inséré avant {anchor}")


def insert_before_close(path: Path, entry: str, guard: str) -> None:
    """Ajoute une ligne avant la dernière accolade/parenthèse fermante."""
    text = path.read_text(encoding="utf-8")
    if guard in text:
        print(f"  {path.name}: déjà présent")
        return
    stripped = text.rstrip()
    idx = max(stripped.rfind("}"), stripped.rfind(")"))
    if idx < 0:
        raise SystemExit(f"{path.name}: fin de bloc introuvable")
    text = text[:idx] + entry + "\n" + text[idx:]
    path.write_text(text, encoding="utf-8")
    print(f"  {path.name}: entrée ajoutée")


def install(gcsim: Path, key: str) -> bool:
    src = CHARS / key
    if not src.is_dir():
        raise SystemExit(f"perso inconnu dans {CHARS}: {key}")
    pretty = key.capitalize()

    dest = gcsim / "internal/characters" / key
    if dest.exists():
        print(f"{key}: DÉJÀ dans gcsim en amont — on garde leur version")
        return False

    print(f"{key}: installation")
    dest.mkdir(parents=True)
    for f in sorted(src.glob("*.go")):
        shutil.copy2(f, dest / f.name)
    print(f"  {len(list(dest.glob('*.go')))} fichiers copiés")

    insert_sorted_triple(gcsim / "pkg/core/keys/character.dm.go", key, pretty)
    insert_before_close(
        gcsim / "pkg/shortcut/character.dm.go",
        f'\t"{key}":                  keys.{pretty},',
        f'"{key}":',
    )
    insert_before_close(
        gcsim / "internal/services/assets/character.dm.go",
        f'\t"{key}":         "UI_AvatarIcon_{pretty}",',
        f'"{key}":',
    )
    insert_before_close(
        gcsim / "pkg/simulation/imports.character.dm.go",
        f'\t_ "github.com/genshinsim/gcsim/internal/characters/{key}"',
        f"/characters/{key}\"",
    )
    return True


WEAPONS = TOOL / "gcsim_weapon"


def install_weapon(gcsim: Path, key: str) -> bool:
    """Même principe pour une arme : sans elle, la sim du perso échoue."""
    src = WEAPONS / key
    cls = (src / "_class").read_text(encoding="utf-8").strip()
    pretty = (src / "_ident").read_text(encoding="utf-8").strip()
    dest = gcsim / "internal/weapons" / cls / key
    if dest.exists():
        print(f"{key}: arme déjà dans gcsim — on garde leur version")
        return False

    print(f"{key}: installation (arme {cls})")
    dest.mkdir(parents=True)
    for f in sorted(src.glob("*.go")):
        shutil.copy2(f, dest / f.name)

    insert_sorted_triple(gcsim / "pkg/core/keys/weapon.dm.go", key, pretty)
    insert_before_close(
        gcsim / "pkg/shortcut/weapon.dm.go",
        f'\t"{key}":                       keys.{pretty},',
        f'"{key}":',
    )
    insert_before_close(
        gcsim / "internal/services/assets/weapon.dm.go",
        f'\t"{key}":                       "UI_EquipIcon_{pretty}",',
        f'"{key}":',
    )
    insert_before_close(
        gcsim / "pkg/simulation/imports.weapon.dm.go",
        f'\t_ "github.com/genshinsim/gcsim/internal/weapons/{cls}/{key}"',
        f"/weapons/{cls}/{key}\"",
    )
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    gcsim = Path(sys.argv[1])
    if not (gcsim / "pkg/core/keys/character.dm.go").exists():
        raise SystemExit(f"pas une source gcsim : {gcsim}")
    wanted = sys.argv[2:] or sorted(p.name for p in CHARS.iterdir()
                                    if p.is_dir())
    done = [k for k in wanted if install(gcsim, k)]
    print(f"\n{len(done)}/{len(wanted)} perso(s) installé(s) : "
          + (", ".join(done) if done else "aucun"))

    if WEAPONS.is_dir():
        wkeys = sorted(p.name for p in WEAPONS.iterdir() if p.is_dir())
        wdone = [k for k in wkeys if install_weapon(gcsim, k)]
        print(f"{len(wdone)}/{len(wkeys)} arme(s) installée(s) : "
              + (", ".join(wdone) if wdone else "aucune"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
