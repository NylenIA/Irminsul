"""Contrôle syntaxique léger des fichiers Dart (pas de Flutter en local).

Ne remplace PAS `flutter analyze` (qui tourne en CI) : il attrape les erreurs
grossières avant un push — délimiteurs déséquilibrés, chaîne non fermée,
commentaire de bloc non fermé — en tokenisant correctement les chaînes Dart
(simple/double, raw, triple, et interpolation `${...}` imbriquée).

    python tool/dart_sanity.py [chemin...]   # défaut : lib/
"""

from __future__ import annotations

import pathlib
import re
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


def strip_code(src: str) -> str:
    """Retire commentaires et chaînes : ne reste que du code exécutable."""
    out, i, n = [], 0, len(src)
    string: StrState | None = None
    interp: list[tuple[int, StrState]] = []
    depth = 0
    while i < n:
        c = src[i]
        if string is None:
            if src.startswith("//", i):
                nl = src.find("\n", i)
                if nl == -1:
                    break
                i = nl
                continue
            if src.startswith("/*", i):
                end = src.find("*/", i + 2)
                if end == -1:
                    break
                i = end + 2
                continue
            raw, j = False, i
            if c == "r" and i + 1 < n and src[i + 1] in "\"'":
                raw, j = True, i + 1
            if src[j] in "\"'":
                q = src[j]
                triple = src.startswith(q * 3, j)
                string = (q, triple, raw, 0)
                i = j + (3 if triple else 1)
                out.append(" ")
                continue
            if c in OPEN:
                depth += 1
            elif c in CLOSE:
                depth -= 1
                if interp and c == "}" and depth == interp[-1][0]:
                    string = interp.pop()[1]
            out.append(c)
            i += 1
            continue
        q, triple, raw, _ = string
        if not raw and c == "\\":
            i += 2
            continue
        if not raw and src.startswith("${", i):
            interp.append((depth, string))
            depth += 1
            string = None
            i += 2
            continue
        if src.startswith(q * 3, i) if triple else c == q:
            string = None
            i += 3 if triple else 1
            continue
        if c == "\n":
            out.append("\n")
        i += 1
    return "".join(out)


DECL = re.compile(
    r"^(?:abstract\s+|sealed\s+|final\s+|base\s+|interface\s+|mixin\s+)*"
    r"(?:class|enum|extension|typedef|mixin)\s+([A-Z]\w*)", re.M)
TOP_VAR = re.compile(r"^final\s+([a-z]\w*(?:Provider|Service))\s*=", re.M)
IMPORT = re.compile(r'import\s+"([^"]+)"([^;]*);')


def check_imports(root: pathlib.Path) -> list[str]:
    """Détecte un symbole DU PROJET utilisé sans importer son fichier.

    C'est la panne qui casse le build alors que la syntaxe est correcte
    (« Type 'PlayerBox' not found »). On ne vérifie que les symboles définis
    dans le projet : aucun faux positif venant du SDK ou des paquets.
    """
    files = sorted(root.rglob("*.dart"))
    raw = {f: f.read_text(encoding="utf-8") for f in files}
    # les imports vivent dans des CHAÎNES : on les lit sur la source brute,
    # et on cherche les identifiants sur la source nettoyée.
    code = {f: strip_code(src) for f, src in raw.items()}
    owner: dict[str, set[pathlib.Path]] = {}
    for f, src in code.items():
        for m in list(DECL.finditer(src)) + list(TOP_VAR.finditer(src)):
            owner.setdefault(m.group(1), set()).add(f.resolve())

    errs: list[str] = []
    for f, src in code.items():
        visible = {f.resolve()}
        shown: dict[pathlib.Path, set[str]] = {}
        for m in IMPORT.finditer(raw[f]):
            target, clause = m.group(1), m.group(2)
            if target.startswith(("package:flutter", "dart:")):
                continue
            p = (f.parent / target).resolve() if not target.startswith("package:") \
                else (root / target.split("/", 1)[-1]).resolve()
            visible.add(p)
            sh = re.search(r"\bshow\s+([\w\s,]+)", clause)
            if sh:
                shown[p] = {s.strip() for s in sh.group(1).split(",")}
        used = set(re.findall(r"\b([A-Z]\w*|[a-z]\w*(?:Provider|Service))\b",
                              src))
        for sym in sorted(used):
            homes = owner.get(sym)
            if not homes:
                continue  # symbole hors projet (SDK, paquet) : non vérifiable
            ok = False
            for h in homes:
                if h not in visible:
                    continue
                allowed = shown.get(h)
                if allowed is None or sym in allowed:
                    ok = True
                    break
            if not ok:
                where = ", ".join(sorted(h.name for h in homes))
                errs.append(f"{f}: « {sym} » utilisé sans importer {where}")
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

    import_errs: list[str] = []
    for r in roots:
        if r.is_dir():
            import_errs += check_imports(r)
    if import_errs:
        print("\nImports manquants (casse le build) :")
        for e in import_errs[:20]:
            print(f"   {e}")

    total = bad + len(import_errs)
    print(f"\n{len(files)} fichier(s) analysé(s) — "
          f"{'OK' if not total else f'{total} problème(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
