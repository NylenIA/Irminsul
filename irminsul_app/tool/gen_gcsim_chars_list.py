"""Génère assets/data/gcsim_chars.json depuis le moteur RÉELLEMENT compilé.

Cette liste dit à l'app quels personnages sont simulables. Tant qu'elle était
écrite à la main, elle mentait dès que le moteur gagnait un perso : la
communauté en ajoute régulièrement, et nous-mêmes en ajoutons (Sandrone,
Zibai, Illuga, Linnea). Résultat vécu : l'app affichait « pas encore
simulable » pour des persos que le moteur savait très bien jouer.

Elle est donc générée en CI à partir de l'arbre gcsim patché, juste après la
compilation — ce qui la rend vraie par construction.

    python tool/gen_gcsim_chars_list.py <chemin-vers-gcsim-src>
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

APP = Path(__file__).resolve().parents[1]

# Dossiers de internal/characters qui ne sont pas des personnages jouables.
NOT_CHARS = {"template", "common", "testhelper"}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1]) / "internal/characters"
    if not src.is_dir():
        raise SystemExit(f"pas une source gcsim : {sys.argv[1]}")

    chars = sorted(
        p.name for p in src.iterdir()
        if p.is_dir() and p.name not in NOT_CHARS and any(p.rglob("*.go"))
    )
    out = APP / "assets/data/gcsim_chars.json"
    previous = []
    if out.exists():
        try:
            previous = json.loads(out.read_text(encoding="utf-8"))["chars"]
        except Exception:
            previous = []

    out.write_text(
        json.dumps(
            {
                "source": "généré depuis internal/characters du moteur compilé",
                "generatedAt": date.today().isoformat(),
                "count": len(chars),
                "chars": chars,
            },
            ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    added = sorted(set(chars) - set(previous))
    removed = sorted(set(previous) - set(chars))
    print(f"OK {len(chars)} personnages simulables")
    if added:
        print(f"   + {', '.join(added)}")
    if removed:
        print(f"   - {', '.join(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
