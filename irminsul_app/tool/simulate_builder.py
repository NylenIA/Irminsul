# Miroir Python du moteur d'equipes : remplit les ARCHETYPES avec TA box,
# puis (optionnel) simule les meilleures avec le vrai gcsim.
#
#   python tool/simulate_builder.py <GOOD.json> [mode] [--sim <gcsim.exe>]
#
# Sert a verifier AVANT de livrer que les equipes proposees sont des equipes
# reelles (pas des combinaisons), et qu'elles tournent vraiment.
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "tool"))

BASELINE_DPS = 22000.0  # reference pour convertir des DGT ajoutes en facteur
LEVEL_MULT = 1446.85
TRANSFORMATIVE = {"superconduct": 1.5, "electro-charged": 2.0,
                  "lunar-charged": 2.0, "lunar-bloom": 2.0,
                  "hyperbloom": 3.0, "burgeon": 3.0, "overloaded": 2.75,
                  "bloom": 2.0, "swirl": 0.6, "shattered": 1.5}


def reaction_damage(reaction, em, bonus):
    base = TRANSFORMATIVE.get(reaction)
    if base is None:
        return 0.0
    em_bonus = 16 * em / (em + 2000)
    return base * LEVEL_MULT * (1 + em_bonus + bonus) * 0.9


def build_quality(oc, b):
    if not oc:
        return 0.0
    lvl = min(max(oc["level"] / 90, 0.15), 1.0)
    tal = min(max((oc["talent"]["skill"] + oc["talent"]["burst"]) / 18, 0.15), 1.0)
    art = 0.35 if not b or b["artifacts"] == 0 else min(max(0.55 + 0.09 * b["artifacts"], 0.55), 1.0)
    wep = 0.55 if not b or b["weaponLevel"] <= 20 else min(max(0.6 + 0.4 * (b["weaponLevel"] / 90), 0.6), 1.0)
    return lvl * 0.35 + tal * 0.25 + art * 0.25 + wep * 0.15


def load_box(path):
    good = json.loads(Path(path).read_text(encoding="utf-8"))
    owned = {c["key"]: c for c in good["characters"]}
    builds = {}
    for w in good["weapons"]:
        if w.get("location"):
            builds.setdefault(w["location"], {"artifacts": 0, "weaponLevel": 0})["weaponLevel"] = w["level"]
    for a in good["artifacts"]:
        if a.get("location"):
            builds.setdefault(a["location"], {"artifacts": 0, "weaponLevel": 0})["artifacts"] += 1
    return good, owned, builds


def fill(arch, tags, by_good, owned, builds, allowed, guests, aspirational):
    """Remplit chaque poste de l'archetype avec le meilleur perso possible."""
    used, team, notes = set(), [], []
    for slot in arch["slots"]:
        want_el = [e.lower() for e in slot.get("elements", [])]
        want_tags = slot.get("tags", [])
        prefer = slot.get("prefer", [])

        def ok(key):
            if key in used or key not in tags:
                return False
            t = tags[key]
            c = by_good.get(key)
            if not c:
                return False
            if allowed and t["element"] not in allowed and c["name"].lower() not in guests:
                return False
            if want_el and t["element"] not in want_el:
                return False
            if want_tags and not any(x in t["tags"] for x in want_tags):
                return False
            return True

        pick, why = None, ""
        for i, key in enumerate(prefer):
            if ok(key) and key in owned:
                pick, why = key, ("titulaire" if i == 0 else "alternative reconnue")
                break
        if not pick:
            cands = [k for k in owned if ok(k)]
            cands.sort(key=lambda k: -build_quality(owned.get(k), builds.get(k)))
            if cands:
                pick, why = cands[0], "meilleur de ta box pour ce poste"
        if not pick and aspirational:
            for key in prefer:
                if ok(key):
                    pick, why = key, "NON POSSEDE"
                    break
        if not pick:
            return None, f"poste « {slot['role']} » impossible a pourvoir"
        used.add(pick)
        team.append({"key": pick, "slot": slot, "why": why})
    return team, ""


def score(arch, team, tags, owned, builds, rules):
    lines, mult = [], 1.0
    elements = {tags[m["key"]]["element"] for m in team}
    keys = {m["key"] for m in team}

    # 1) la reaction de l'archetype est-elle possible ?
    gate = arch.get("gate", [])
    if gate and not (keys & set(gate)):
        return None, ["condition de reaction absente"]

    # 2) bonus du cycle, converti en DGT reels puis en facteur
    boosted = rules.get("boostedReactions", {})
    r = arch.get("reaction")
    if r and r in boosted and arch.get("procs", 0) > 0:
        dmg = reaction_damage(r, 200, boosted[r])
        added = dmg * arch["procs"]
        f = 1 + added / BASELINE_DPS
        mult *= f
        lines.append((f"{r} amplifie ce cycle (~{int(added)} DGT/s ajoutes)", f))
    elif r and r in boosted:
        f = 1.15
        mult *= f
        lines.append((f"{r} favorise par le cycle", f))
    elif boosted:
        mult *= 0.92
        lines.append(("ne profite pas des reactions amplifiees", 0.92))

    for e in rules.get("requiredElements", []):
        if e not in elements:
            mult *= 0.5
            lines.append((f"pas de {e} exige par le contenu", 0.5))
    for tg in rules.get("favoredTags", []):
        if any(tg in tags[m["key"]]["tags"] for m in team):
            mult *= 1.06
            lines.append((f"{tg} utile ici", 1.06))

    boxf, missing, tobuild = 1.0, [], []
    for m in team:
        oc = owned.get(m["key"])
        if not oc:
            missing.append(m["key"])
            boxf *= 0.5
            continue
        q = build_quality(oc, builds.get(m["key"]))
        if oc["level"] < 70 or builds.get(m["key"], {}).get("artifacts", 0) < 5:
            tobuild.append(m["key"])
        boxf *= 0.55 + 0.45 * q
    lines.append(("montage reel de ta box", boxf))
    return mult * boxf, lines, missing, tobuild


def rotation_for(team, gname):
    """Rotation gcsim : supports d'abord, porteur ensuite (jouable a la main)."""
    order = sorted(team, key=lambda m: 0 if not m["slot"].get("carry") and m is not team[0] else 1)
    out = ["while 1 {"]
    for m in order:
        n = gname(m["key"])
        for a in m["slot"].get("actions", ["skill"]):
            out.append(f"    {n} {a};")
    out.append("}")
    return "\n".join(out)


def main():
    good_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "abyss"
    exe = None
    if "--sim" in sys.argv:
        exe = sys.argv[sys.argv.index("--sim") + 1]

    good, owned, builds = load_box(good_path)
    tags = json.loads((APP / "assets/data/character_tags.json").read_text(encoding="utf-8"))
    full = json.loads((APP / "assets/data/characters_full.json").read_text(encoding="utf-8"))["characters"]
    by_good = {c["good"]: c for c in full}
    meta = json.loads((APP / "assets/data/meta_teams.json").read_text(encoding="utf-8"))
    arches = json.loads((APP / "assets/data/team_archetypes.json").read_text(encoding="utf-8"))
    rules = meta["content"][mode]
    allowed = {e.lower() for e in rules.get("allowedElements", [])}
    guests = {g.lower() for g in rules.get("guests", [])}

    results = []
    for arch in arches:
        for aspi in (False, True):
            team, err = fill(arch, tags, by_good, owned, builds, allowed, guests, aspi)
            if not team:
                if not aspi:
                    continue
                break
            sc = score(arch, team, tags, owned, builds, rules)
            if sc is None or sc[0] is None:
                break
            s, lines, missing, tobuild = sc
            results.append((s, arch, team, lines, missing, tobuild))
            if not missing:
                break  # version jouable trouvee : pas besoin de l'aspirationnelle

    results.sort(key=lambda r: (bool(r[4]), -r[0]))
    print(f"=== {mode.upper()} · {len(results)} archétypes jouables ===")
    for s, arch, team, lines, missing, tobuild in results[:5]:
        names = " · ".join(by_good[m["key"]]["name"] for m in team)
        state = ("manque " + ",".join(missing)) if missing else (
            ("à monter " + ",".join(tobuild)) if tobuild else "JOUABLE")
        print(f"\n{s:6.2f}  [{arch['name']}]  {names}   ({state})")
        for m in team:
            print(f"          {m['slot']['role']:28s} {by_good[m['key']]['name']:16s} ({m['why']})")
        print("          " + " · ".join(f"{lb} ×{f:.2f}" for lb, f in lines))

    if exe:
        import gen_gcsim_config as g
        print("\n=== SIMULATION RÉELLE (gcsim, tes builds) ===")
        for s, arch, team, lines, missing, tobuild in results[:3]:
            if missing:
                print(f"  [{arch['name']}] non simulable : perso non possédé")
                continue
            keys = [m["key"] for m in team]
            rot = rotation_for(team, g.gcsim_name if hasattr(g, "gcsim_name") else
                               (lambda k: g.CHAR_MAP.get(k, k.lower())))
            try:
                cfg = g.build_config(good, keys, rot, g.options_for(keys))
            except SystemExit as e:
                print(f"  [{arch['name']}] config impossible : {e}")
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                             encoding="utf-8") as f:
                f.write(cfg)
                path = f.name
            r = subprocess.run([exe, "-c", path], capture_output=True, text=True, timeout=300)
            out = (r.stdout or "") + (r.stderr or "")
            m = re.search(r"resulting in (\d+) dps", out)
            err = re.search(r"error encountered.*|can't execute.*|panic.*", out)
            if m and not err:
                print(f"  [{arch['name']:22s}] {m.group(1):>7} dps réels")
            else:
                msg = (err.group(0) if err else out.strip().split(chr(10))[-1])[:120]
                print(f"  [{arch['name']:22s}] ÉCHEC : {msg}")


if __name__ == "__main__":
    main()
