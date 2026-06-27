#!/usr/bin/env python
"""Projection sûre d'un gros JSON SANS l'injecter entièrement dans le contexte
(GOOD, résultats gcsim, dumps…). Donne la forme (clés, types, longueurs) et, à la
demande, un chemin précis. Cf. MASTER_SPEC §5.3 / §7 (ne jamais charger un GOOD complet).

Usage :
  python scripts/peek_json.py <fichier.json>              # forme top-level
  python scripts/peek_json.py <fichier.json> --path a.b.0 # valeur ciblée (résumée)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def shape(value: Any, depth: int = 0) -> Any:
    if isinstance(value, dict):
        return {k: shape(v, depth + 1) if depth < 1 else _scalar(v) for k, v in list(value.items())[:50]}
    if isinstance(value, list):
        return f"list[{len(value)}]" + ("" if not value else f" of {type(value[0]).__name__}")
    return _scalar(value)


def _scalar(v: Any) -> str:
    if isinstance(v, str):
        return f"str(len={len(v)})" if len(v) > 40 else f"str:{v!r}"
    if isinstance(v, (list, dict)):
        return f"{type(v).__name__}[{len(v)}]"
    return f"{type(v).__name__}:{v}"


def navigate(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(part)
    return cur


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--path", default="")
    args = ap.parse_args()
    p = Path(args.file)
    size = p.stat().st_size
    print(f"[peek] {p} — {size} octets ({round(size/1024)} Ko)")
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    target = navigate(data, args.path) if args.path else data
    print(json.dumps(shape(target), ensure_ascii=False, indent=1)[:2000])


if __name__ == "__main__":
    main()
