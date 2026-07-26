"""Contrôle syntaxique léger des fichiers Dart (pas de Flutter en local).

Ne remplace PAS `flutter analyze` (qui tourne en CI) : il attrape les erreurs
grossières avant un push — délimiteurs déséquilibrés, chaîne non fermée,
commentaire de bloc non fermé — en tokenisant correctement les chaînes Dart
(simple/double, raw, triple, et interpolation `${...}` imbriquée).

    python tool/dart_sanity.py [chemin...]   # défaut : lib/
"""

from __future__ import annotations

import pathlib
import sys

OPEN = "([{"
CLOSE = ")]}"
PAIR = {")": "(", "]": "[", "}": "{"}

# état d'une chaîne en cours : (quote, triple, raw, ligne d'ouverture)
StrState = tuple[str, bool, bool, int]


def scan(src: str) -> list[str]:
    """Retourne la liste des problèmes trouvés (vide = OK)."""
    errs: list[str] = []
    stack: list[tuple[str, int]] = []  # délimiteurs ouverts (char, ligne)
    interp: list[tuple[int, StrState]] = []  # ${...} en cours
    string: StrState | None = None
    i, line, n = 0, 1, len(src)

    while i < n:
        c = src[i]

        if string is None:
            if c == "\n":
                line += 1
                i += 1
                continue
            if src.startswith("//", i):
                nl = src.find("\n", i)
                if nl == -1:
                    break
                i = nl
                continue
            if src.startswith("/*", i):
                end = src.find("*/", i + 2)
                if end == -1:
                    errs.append(f"L{line}: commentaire de bloc non fermé")
                    break
                line += src.count("\n", i, end)
                i = end + 2
                continue
            # ouverture de chaîne (préfixe r éventuel)
            raw, j = False, i
            if c == "r" and i + 1 < n and src[i + 1] in "\"'":
                raw, j = True, i + 1
            if src[j] in "\"'":
                q = src[j]
                triple = src.startswith(q * 3, j)
                string = (q, triple, raw, line)
                i = j + (3 if triple else 1)
                continue
            if c in OPEN:
                stack.append((c, line))
            elif c in CLOSE:
                if not stack:
                    errs.append(f"L{line}: « {c} » sans ouverture")
                elif stack[-1][0] != PAIR[c]:
                    o, ol = stack.pop()
                    errs.append(f"L{line}: « {c} » ferme « {o} » (L{ol})")
                else:
                    stack.pop()
                    # fin d'une interpolation → on repart dans la chaîne
                    if interp and c == "}" and len(stack) == interp[-1][0]:
                        string = interp.pop()[1]
            i += 1
            continue

        # --- à l'intérieur d'une chaîne ---
        q, triple, raw, opened = string
        if c == "\n":
            line += 1
            if not triple:
                errs.append(f"L{opened}: chaîne non fermée en fin de ligne")
                string = None
            i += 1
            continue
        if not raw and c == "\\":
            i += 2
            continue
        if not raw and src.startswith("${", i):
            interp.append((len(stack), string))
            stack.append(("{", line))
            string = None
            i += 2
            continue
        if not raw and c == "$" and i + 1 < n and (
            src[i + 1].isalpha() or src[i + 1] == "_"
        ):
            i += 1
            while i < n and (src[i].isalnum() or src[i] == "_"):
                i += 1
            continue
        if src.startswith(q * 3, i) if triple else c == q:
            string = None
            i += 3 if triple else 1
            continue
        i += 1

    if string is not None:
        errs.append(f"L{string[3]}: chaîne non fermée en fin de fichier")
    for o, ol in stack:
        errs.append(f"L{ol}: « {o} » jamais fermé")
    return errs


def main(argv: list[str]) -> int:
    roots = [pathlib.Path(a) for a in argv[1:]] or [pathlib.Path("lib")]
    files: list[pathlib.Path] = []
    for r in roots:
        files.extend(sorted(r.rglob("*.dart")) if r.is_dir() else [r])

    bad = 0
    for f in files:
        errs = scan(f.read_text(encoding="utf-8"))
        if errs:
            bad += 1
            print(f"\n{f}")
            for e in errs[:10]:
                print(f"   {e}")
    print(f"\n{len(files)} fichier(s) analysé(s) — "
          f"{'OK' if not bad else f'{bad} avec problème(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
