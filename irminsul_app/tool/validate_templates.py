# Valide les 15 rotations par SIMULATION avant embarquement.
# - GOOD reel si le joueur possede les 4 titulaires, sinon GOOD synthetique
#   (90/9/9/9, arme Favonius, artefacts standards) : valide la SYNTAXE et
#   l'execution de la rotation (pas les chiffres).
# Usage : python tool/validate_templates.py <gcsim.exe> [GOOD reel]
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gen_gcsim_config as g  # noqa: E402
from templates_all import TEMPLATES  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
full = json.loads(
    (HERE / "assets/data/characters_full.json").read_text(encoding="utf-8"))
BY_GOOD = {c["good"]: c for c in full["characters"]}

FAV = {
    "Épée à une main": "FavoniusSword",
    "Épée à deux mains": "FavoniusGreatsword",
    "Arme d'hast": "FavoniusLance",
    "Arc": "FavoniusWarbow",
    "Catalyseur": "FavoniusCodex",
    # libellés FR possibles selon genshin-db
    "Épée": "FavoniusSword",
    "Lance": "FavoniusLance",
}


def synth_good(good_keys):
    """GOOD synthetique : titulaires 90/9/9/9 + Favonius 90 + artefacts std."""
    chars, weapons, artifacts = [], [], []
    for k in good_keys:
        c = BY_GOOD[k]
        chars.append({
            "key": k, "level": 90, "ascension": 6, "constellation": 0,
            "talent": {"auto": 9, "skill": 9, "burst": 9},
        })
        weapons.append({
            "key": FAV.get(c["weaponType"], "FavoniusSword"),
            "level": 90, "ascension": 6, "refinement": 1, "location": k,
        })
        mains = ["hp", "atk", "atk_", "atk_", "critRate_"]
        for slot, main in zip(
                ["flower", "plume", "sands", "goblet", "circlet"], mains):
            artifacts.append({
                "setKey": "GladiatorsFinale", "slotKey": slot, "rarity": 5,
                "level": 20, "mainStatKey": main, "location": k,
                "substats": [
                    {"key": "critRate_", "value": 6.6},
                    {"key": "critDMG_", "value": 13.2},
                    {"key": "atk_", "value": 9.9},
                    {"key": "enerRech_", "value": 11.0},
                ],
            })
    return {"format": "GOOD", "version": 3, "characters": chars,
            "weapons": weapons, "artifacts": artifacts}


def main():
    exe = sys.argv[1]
    real = (json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
            if len(sys.argv) > 2 else None)
    owned = ({c["key"] for c in real["characters"]} if real else set())

    ok, ko = [], []
    for tid, tpl in TEMPLATES.items():
        use_real = real is not None and all(k in owned for k in tpl["chars"])
        good = real if use_real else synth_good(tpl["chars"])
        src = "REEL" if use_real else "synth"
        try:
            cfg = g.build_config(good, tpl["chars"], tpl["rotation"],
                                 g.options_for(tpl["chars"]))
        except SystemExit as e:
            ko.append((tid, src, f"config: {e}"))
            continue
        with tempfile.NamedTemporaryFile(
                "w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(cfg)
            path = f.name
        r = subprocess.run([exe, "-c", path], capture_output=True,
                           text=True, timeout=300)
        out = (r.stdout or "") + (r.stderr or "")
        m = re.search(r"resulting in (\d+) dps", out)
        err = re.search(r"error encountered.*|can't execute.*|panic.*", out)
        if m and not err:
            ok.append((tid, src, int(m.group(1))))
            print(f"OK  {tid:22s} [{src:5s}] {m.group(1)} dps")
        else:
            msg = (err.group(0) if err else out.strip().split("\n")[-1])[:110]
            ko.append((tid, src, msg))
            print(f"KO  {tid:22s} [{src:5s}] {msg}")

    print(f"\n=== {len(ok)} OK / {len(ko)} KO ===")
    sys.exit(1 if ko else 0)


if __name__ == "__main__":
    main()
