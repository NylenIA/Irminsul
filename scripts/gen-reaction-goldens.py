#!/usr/bin/env python3
"""Goldens des réactions élémentaires depuis le VRAI moteur Python (src/irminsul/reaction.py).

Formules KQM versionnées (TRANSFORMATIVE_BASE/AMPLIFYING_BASE, bonus EM 16x/(x+2000) et
2.78x/(x+1400)). Aucune valeur inventée. Reproductible :
    python scripts/gen-reaction-goldens.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from irminsul.reaction import (  # noqa: E402
    amplifying_multiplier,
    lunar_reaction,
    transformative_reaction,
)

OUT = ROOT / "packages" / "engine-client" / "tests" / "reaction.goldens.json"

AMPLIFYING_CASES = [
    dict(reaction="forward-vaporize", elemental_mastery=0),
    dict(reaction="forward-vaporize", elemental_mastery=187),
    dict(reaction="reverse-vaporize", elemental_mastery=320, reaction_bonus=0.15),
    dict(reaction="forward-melt", elemental_mastery=1000),
    dict(reaction="reverse-melt", elemental_mastery=40, reaction_bonus=-0.5),  # clamp bas
]

TRANSFORMATIVE_CASES = [
    dict(reaction="swirl", elemental_mastery=0),
    dict(reaction="swirl", elemental_mastery=800, enemy_resistance=-0.2),
    dict(reaction="overloaded", elemental_mastery=187),
    dict(reaction="electro-charged", elemental_mastery=320, reaction_bonus=0.4),
    dict(reaction="superconduct", elemental_mastery=100, enemy_resistance=0.75),  # frontière RES
    dict(reaction="hyperbloom", elemental_mastery=1000, reaction_bonus=0.4),
    dict(reaction="burgeon", elemental_mastery=600),
    dict(reaction="bloom", elemental_mastery=250, enemy_resistance=0.0),  # frontière RES=0
    dict(reaction="burning", elemental_mastery=0, level_multiplier=1077.44),  # niveau ≠ 90
    dict(reaction="shattered", elemental_mastery=50),
    # Alias Python (audit Codex) : mêmes valeurs, clé renvoyée telle quelle
    dict(reaction="overload", elemental_mastery=120),
    dict(reaction="shatter", elemental_mastery=0),
]


LUNAR_CASES = [
    # Baseline LC : 1 contributeur, point EM publié (1000 -> +200 %), RES 0.
    dict(reaction="lunar-charged", contributors=[dict(elemental_mastery=1000)], enemy_resistance=0.0),
    # Tri : fourni dans le mauvais ordre (faible d'abord), RES 10 % par défaut.
    dict(
        reaction="lunar-charged",
        contributors=[dict(elemental_mastery=0), dict(elemental_mastery=2000)],
    ),
    # 4 contributeurs mixtes (crit, bonus base/réaction, clamp crit_rate).
    dict(
        reaction="lunar-charged",
        contributors=[
            dict(elemental_mastery=500, crit_rate=0.6, crit_damage=1.2),
            dict(elemental_mastery=187, reaction_bonus=0.4),
            dict(elemental_mastery=1500, crit_rate=1.5, crit_damage=0.5, base_dmg_bonus=0.25),
            dict(),
        ],
        enemy_resistance=-0.2,
    ),
    # Niveau != 90 + frontière RES élevée.
    dict(
        reaction="lunar-charged",
        contributors=[dict(elemental_mastery=320, crit_rate=0.31, crit_damage=0.884)],
        level_multiplier=1077.44,
        enemy_resistance=0.75,
    ),
    # LCrys : base 1.6, baseline EM publiée.
    dict(
        reaction="lunar-crystallize",
        contributors=[dict(elemental_mastery=1000)],
        enemy_resistance=0.0,
    ),
    # LCrys : 2 contributeurs avec crit (Hydro applier + Geo trigger).
    dict(
        reaction="lunar-crystallize",
        contributors=[
            dict(elemental_mastery=800, crit_rate=0.7, crit_damage=1.4),
            dict(elemental_mastery=120, crit_rate=0.05, crit_damage=0.5),
        ],
    ),
]


def main() -> None:
    goldens = {
        "source": "src/irminsul/reaction.py (formules KQM ; niveau 90 = 1446.85)",
        "generator": "scripts/gen-reaction-goldens.py",
        "amplifying": [
            {"inputs": c, "expected": amplifying_multiplier(**c).to_dict()}
            for c in AMPLIFYING_CASES
        ],
        "transformative": [
            {"inputs": c, "expected": transformative_reaction(**c).to_dict()}
            for c in TRANSFORMATIVE_CASES
        ],
        "lunar": [
            {"inputs": c, "expected": lunar_reaction(**c).to_dict()}
            for c in LUNAR_CASES
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(goldens, indent=2), encoding="utf-8")
    print(
        f"{len(AMPLIFYING_CASES)} amplifiantes + {len(TRANSFORMATIVE_CASES)} transformatives "
        f"+ {len(LUNAR_CASES)} lunaires -> {OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
