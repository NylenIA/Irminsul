#!/usr/bin/env python
"""Index léger et incrémental du dépôt pour des lectures CIBLÉES (cf. §3, §5.3).

Construit `.irminsul/index/repo-index.json` : par fichier suivi → taille, lignes,
et pour les .py les symboles top-level (fonctions/classes) avec leur ligne. Évite
de relire des fichiers entiers : on cible un symbole puis on étend si besoin.

Déterministe, stdlib uniquement. Usage : python scripts/index_repo.py
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".irminsul" / "index" / "repo-index.json"


def tracked_files() -> list[str]:
    try:
        res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True)  # noqa: S603,S607
        return [f for f in res.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def py_symbols(path: Path) -> list[dict[str, object]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return []
    out: list[dict[str, object]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "func"
            out.append({"name": node.name, "kind": kind, "line": node.lineno})
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        out.append({"name": f"{node.name}.{sub.name}", "kind": "method",
                                    "line": sub.lineno})
    return out


def build() -> dict[str, object]:
    files: dict[str, object] = {}
    total_lines = 0
    for rel in tracked_files():
        p = ROOT / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.count("\n") + 1
        total_lines += lines
        entry: dict[str, object] = {"bytes": p.stat().st_size, "lines": lines}
        if rel.endswith(".py"):
            syms = py_symbols(p)
            if syms:
                entry["symbols"] = syms
        files[rel] = entry
    return {"file_count": len(files), "total_lines": total_lines, "files": files}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    py = sum(1 for f in data["files"] if f.endswith(".py"))
    print(f"[index] {data['file_count']} fichiers, {data['total_lines']} lignes, "
          f"{py} modules Python → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
