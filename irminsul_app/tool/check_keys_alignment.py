"""Vérifie que les listes de clés de gcsim restent ALIGNÉES après nos patchs.

`pkg/core/keys/character.dm.go` (et son équivalent armes) contient trois
listes parallèles : les constantes (dont l'index vaut la valeur), les noms en
minuscules, et le tableau des valeurs. Insérer une clé dans une seule liste,
ou à la mauvaise position, décale tout silencieusement — un perso jouerait le
kit d'un autre.

    python tool/check_keys_alignment.py <chemin-vers-gcsim> [clé ...]

Les clés passées en argument doivent être présentes et cohérentes ; sans
argument, seule la cohérence globale est vérifiée. Sort 1 si quelque chose
cloche.
"""

import re
import sys
from pathlib import Path

FILES = [
    ("personnages", "pkg/core/keys/character.dm.go"),
    ("armes", "pkg/core/keys/weapon.dm.go"),
]


def check(path: Path, label: str, wanted: list[str]) -> bool:
    if not path.exists():
        print(f"!! {label}: fichier absent ({path})")
        return False
    t = path.read_text(encoding="utf-8")
    consts = [c[1] for c in re.findall(r"^\t(\w+) +// ([a-z0-9]*)$", t, re.M)]
    names = re.findall(r'^\t"([a-z0-9]+)",$', t, re.M)
    # la liste des valeurs contient une sentinelle (NoChar / NoWeapon) qui n'a
    # pas de nom : on la retire avant de comparer les longueurs.
    vals = [v for v in re.findall(r"^\t([A-Za-z0-9]+),$", t, re.M)
            if v.lower() in set(names)]
    ok = True

    # 1) même longueur : l'invariant qui casse en premier
    if not (len(consts) == len(names) == len(vals)):
        print(f"!! {label}: longueurs différentes "
              f"(const {len(consts)}, noms {len(names)}, valeurs {len(vals)})")
        ok = False

    # 2) même ordre entre constantes et noms
    for i, (c, n) in enumerate(zip(consts, names)):
        if c != n:
            print(f"!! {label}: décalage à l'index {i} : "
                  f"const « {c} » vs nom « {n} »")
            ok = False
            break

    # 3) les clés demandées sont bien présentes au même endroit partout
    for key in wanted:
        if key not in names:
            continue  # cette clé n'appartient pas à ce fichier
        if key not in consts or consts.index(key) != names.index(key):
            print(f"!! {label}: « {key} » mal inséré")
            ok = False

    if ok:
        print(f"{label}: alignement OK ({len(names)} clés)")
    return ok


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    wanted = [k.lower() for k in sys.argv[2:]]
    results = [check(root / rel, label, wanted) for label, rel in FILES]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
