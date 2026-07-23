#!/usr/bin/env python3
"""Recalcule l'avancement Irminsul depuis docs/project/PROJECT_PROGRESS.json (matrice versionnée).

Reproductible : le pourcentage vient des données, jamais d'un chiffre écrit à la main.
Usage : python scripts/project_progress.py
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "project" / "PROJECT_PROGRESS.json"
OUT = ROOT / "docs" / "project" / "PROJECT_PROGRESS.md"


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    domains = d["domains"]
    wsum = sum(x["weight"] for x in domains)
    mwsum = sum(x["mvpWeight"] for x in domains)
    if wsum != 100 or mwsum != 100:
        raise SystemExit(f"Les poids doivent sommer à 100 (weight={wsum}, mvpWeight={mwsum}).")

    vision = sum(x["weight"] * x["score"] for x in domains) / 100
    mvp = sum(x["mvpWeight"] * x["score"] for x in domains) / 100

    lines = [
        "# Avancement Irminsul — recalculé (reproductible)",
        "",
        f"> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json`"
        f" le {d['updatedAt']}. Branche `{d['branch']}`. Ne pas éditer à la main.",
        "",
        "## Scores",
        f"- **MVP utilisable : {mvp:.0f}%**",
        f"- **Vision complète : {vision:.0f}%**",
        f"- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).",
        f"- Échelle : {d['scale']}",
        "",
        "## Détail par domaine",
        "| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |",
        "|---|--:|--:|--:|---|---|---|",
    ]
    for x in domains:
        lines.append(
            f"| {x['label']} | {x['weight']} | {x['mvpWeight']} | {x['score']} "
            f"| {x['confidence']} | {x['evidence']} | {x['blockers']} |"
        )
    lines += ["", "_Recalcule : `python scripts/project_progress.py`._", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"MVP utilisable : {mvp:.0f}%  |  Vision complète : {vision:.0f}%")
    print(f"-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
