#!/usr/bin/env python3
"""Génère les goldens du contrat EngineClient depuis le VRAI moteur Python (src/irminsul/damage.py).

Provenance traçable : aucune valeur inventée — chaque `expected` sort de calculate_direct_hit,
lui-même couvert par les tests goldens vérifiés en jeu. Reproductible :
    python scripts/gen-engine-goldens.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from irminsul.damage import calculate_direct_hit  # noqa: E402

OUT = ROOT / "packages" / "engine-client" / "tests" / "direct-hit.goldens.json"

CASES: list[dict[str, float | int]] = [
    # Cas nominal type carry (crit build, bonus élémentaire goblet)
    dict(scaling=2.0, scaling_stat=2000, crit_rate=0.5, crit_damage=1.0,
         damage_bonus=0.466, enemy_level=100, attacker_level=90, enemy_resistance=0.1),
    # Défauts purs (base 5%/50% crit, RES 10%)
    dict(scaling=1.0, scaling_stat=1000),
    # Crit garanti + réduction DEF + RES négative (shred sous 0)
    dict(scaling=3.5, scaling_stat=2500, crit_rate=1.0, crit_damage=2.0,
         damage_bonus=0.616, defense_reduction=0.2, enemy_resistance=-0.05),
    # RES élevée (>=75% : branche 1/(4R+1)) + ignore DEF + vaporisation avant EM
    dict(scaling=1.5, scaling_stat=1800, enemy_resistance=0.9, defense_ignore=0.3,
         amplifying_reaction_multiplier=1.5, reaction_bonus=0.15),
    # Flat base damage + vulnérabilité + crit_rate clampé (entrée 1.4 -> 1.0)
    dict(scaling=0.8, scaling_stat=1200, flat_base_damage=500, vulnerability_multiplier=1.2,
         crit_rate=1.4, crit_damage=0.8),
]


def main() -> None:
    goldens = []
    for case in CASES:
        result = calculate_direct_hit(**case)
        goldens.append({"inputs": case, "expected": result.to_dict()})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "src/irminsul/damage.py::calculate_direct_hit (registre mechanics: verified)",
        "generator": "scripts/gen-engine-goldens.py",
        "cases": goldens,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"{len(goldens)} goldens -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
