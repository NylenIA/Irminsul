"""Non-régression : intégrité du dépôt — détecte la disparition d'un fichier CRITIQUE.

Motivation : incident du 2026-06-29 où `app/src/engine.ts` a été supprimé hors mission
par un processus externe (Codex orphelin en workspace-write) entre un build vert et le
commit. Ce test échoue IMMÉDIATEMENT (validate.sh + CI) si l'un de ces fichiers manque,
empêchant qu'une suppression accidentelle passe inaperçue. Cf. docs/reviews/INCIDENT_engine_ts.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Fichiers porteurs du parcours import→perso→arme/artéfacts→stats finales→calcul (et build app).
CRITICAL_FILES = [
    # Moteur Python
    "src/irminsul/basestats.py",
    "src/irminsul/weaponstats.py",
    "src/irminsul/talentstats.py",
    "src/irminsul/charstats.py",
    "src/irminsul/damage.py",
    "src/irminsul/reaction.py",
    "src/irminsul/quickcalc.py",
    "src/irminsul/sidecar.py",
    "src/irminsul/account_ipc.py",
    # Données mécaniques embarquées (sourcées, versionnées)
    "data/mechanics/source-registry.json",
    "data/mechanics/character-basestats.json",
    "data/mechanics/weapon-basestats.json",
    "data/mechanics/talent-multipliers.json",
    # Frontend + pont Rust + build sidecar
    "app/src/engine.ts",
    "app/src/views/QuickCalc.tsx",
    "app/src-tauri/src/lib.rs",
    "tools/build_sidecar.py",
    "tools/extract_basestats.py",
    "tools/extract_weapon_basestats.py",
    "tools/extract_talent_multipliers.py",
    "scripts/validate.sh",
]


@pytest.mark.parametrize("rel", CRITICAL_FILES)
def test_critical_file_present_and_nonempty(rel: str) -> None:
    p = REPO / rel
    assert p.is_file(), f"FICHIER CRITIQUE MANQUANT: {rel} (suppression accidentelle ?)"
    assert p.stat().st_size > 0, f"fichier critique vide: {rel}"


def test_build_sidecar_bundles_all_mechanics_data() -> None:
    # Garantit que tout fichier de données mécaniques est bien embarqué dans le sidecar
    # (sinon le moteur packagé perdrait silencieusement une capacité).
    bs = (REPO / "tools" / "build_sidecar.py").read_text(encoding="utf-8")
    for fname in ("source-registry.json", "character-basestats.json",
                  "weapon-basestats.json", "talent-multipliers.json"):
        assert fname in bs, f"{fname} non bundlé dans build_sidecar.py"
