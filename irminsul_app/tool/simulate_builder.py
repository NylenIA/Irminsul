# Miroir Python de lib/src/data/team_builder.dart : rejoue l'optimiseur sur
# le GOOD REEL avant de livrer, pour voir ce que le joueur verra vraiment.
# (Meme methode que simulate_match.py : elle a trouve tous les bugs jusqu'ici.)
#
#   python tool/simulate_builder.py <GOOD.json> [abyss|theater|onslaught]
import json
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]

TAG_VALUE = {
    "atk_buff": 0.26, "dmg_buff": 0.24, "res_shred": 0.22, "em_buff": 0.14,
    "heal": 0.12, "shield": 0.12, "offfield": 0.16, "energy": 0.10,
    "crowd": 0.06, "interrupt": 0.05, "nightsoul": 0.04,
}
PAIRS = {
    "vaporize": ["pyro", "hydro"], "melt": ["pyro", "cryo"],
    "overloaded": ["pyro", "electro"], "superconduct": ["cryo", "electro"],
    "electro-charged": ["hydro", "electro"], "frozen": ["hydro", "cryo"],
    "bloom": ["hydro", "dendro"], "hyperbloom": ["hydro", "dendro", "electro"],
    "burgeon": ["hydro", "dendro", "pyro"], "burning": ["pyro", "dendro"],
    "aggravate": ["dendro", "electro"], "quicken": ["dendro", "electro"],
    "spread": ["dendro", "electro"], "swirl": ["anemo"],
    "crystallize": ["geo"], "lunar-charged": ["hydro", "electro"],
    "lunar-bloom": ["hydro", "dendro"], "stellar-conduct": ["cryo", "electro"],
}


def build_quality(oc, b):
    if not oc:
        return 0.0
    lvl = min(max(oc["level"] / 90, 0.15), 1.0)
    tal = min(max((oc["talent"]["skill"] + oc["talent"]["burst"]) / 18, 0.15), 1.0)
    art = 0.35 if not b or b["artifacts"] == 0 else min(max(0.55 + 0.09 * b["artifacts"], 0.55), 1.0)
    wep = 0.55 if not b or b["weaponLevel"] <= 20 else min(max(0.6 + 0.4 * (b["weaponLevel"] / 90), 0.6), 1.0)
    return lvl * 0.35 + tal * 0.25 + art * 0.25 + wep * 0.15


def main():
    good = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    mode = sys.argv[2] if len(sys.argv) > 2 else "abyss"
    tags = json.loads((APP / "assets/data/character_tags.json").read_text(encoding="utf-8"))
    full = json.loads((APP / "assets/data/characters_full.json").read_text(encoding="utf-8"))["characters"]
    meta = json.loads((APP / "assets/data/meta_teams.json").read_text(encoding="utf-8"))
    rules = meta["content"][mode]

    by_good = {c["good"]: c for c in full}
    owned = {c["key"]: c for c in good["characters"]}
    builds = {}
    for w in good["weapons"]:
        if w.get("location"):
            builds.setdefault(w["location"], {"artifacts": 0, "weaponLevel": 0})["weaponLevel"] = w["level"]
    for a in good["artifacts"]:
        if a.get("location"):
            builds.setdefault(a["location"], {"artifacts": 0, "weaponLevel": 0})["artifacts"] += 1

    allowed = {e.lower() for e in rules.get("allowedElements", [])}
    guests = {g.lower() for g in rules.get("guests", [])}
    boosted = rules.get("boostedReactions", {})
    required = rules.get("requiredElements", [])
    favored = rules.get("favoredTags", [])

    def ok_elem(c):
        t = tags.get(c["good"])
        return (not allowed) or (t and t["element"] in allowed) or c["name"].lower() in guests

    pool = [c for c in full if c["good"] in tags and ok_elem(c)]
    carries = sorted(
        [(c, build_quality(owned.get(c["good"]), builds.get(c["good"])), c["good"] in owned)
         for c in pool if tags[c["good"]]["carry"]],
        key=lambda x: (not x[2], -x[1]))
    supports = sorted(
        [(c, sum(TAG_VALUE.get(t, 0) for t in tags[c["good"]]["tags"]) *
          ((0.4 + build_quality(owned.get(c["good"]), builds.get(c["good"]))) if c["good"] in owned else 0.35))
         for c in pool if not tags[c["good"]]["carry"] or c["good"] not in owned],
        key=lambda x: -x[1])[:18]

    results = {}
    for carry, cq, cowned in carries[:8]:
        cand = [s for s, _ in supports if s["id"] != carry["id"]]
        for i in range(len(cand)):
            for j in range(i + 1, len(cand)):
                for k in range(j + 1, len(cand)):
                    team = [carry, cand[i], cand[j], cand[k]]
                    elements = {tags[c["good"]]["element"] for c in team}
                    mult, why = 1.0, []
                    carry_el = tags[carry["good"]]["element"]
                    appliers = {tags[c["good"]]["element"] for c in team
                                if "offfield" in tags[c["good"]]["tags"]
                                or tags[c["good"]]["carry"]}
                    best, best_name, second = 0.0, "", 0.0
                    for r, boost in boosted.items():
                        need = PAIRS.get(r, [])
                        if not need or not all(e in elements for e in need):
                            continue
                        carried = carry_el in need
                        fed = all(e in appliers for e in need)
                        if not carried and not fed:
                            continue
                        f = 1 + boost * (0.30 if carried else 0.15)
                        if f > best:
                            best, best_name, second = f, r, best
                        elif f > second:
                            second = f
                    if best:
                        mult *= best
                        why.append(f"{best_name} amplifie")
                        if second:
                            mult *= 1.05
                            why.append("2e reaction dispo")
                    elif boosted:
                        mult *= 0.80
                        why.append("aucune reaction du cycle")
                    for e in required:
                        if e not in elements:
                            mult *= 0.45
                            why.append(f"pas de {e}")
                    for tg in favored:
                        if any(tg in tags[c["good"]]["tags"] for c in team):
                            mult *= 1.08
                            why.append(f"{tg} ok")
                    boxf, missing, tobuild = 1.0, [], []
                    for c in team:
                        oc = owned.get(c["good"])
                        if not oc:
                            missing.append(c["name"])
                            boxf *= 0.55
                            continue
                        q = build_quality(oc, builds.get(c["good"]))
                        if oc["level"] < 70 or builds.get(c["good"], {}).get("artifacts", 0) < 5:
                            tobuild.append(c["name"])
                        boxf *= 0.55 + 0.45 * q
                    seen, support = {}, 0.0
                    for c in team:
                        if c["id"] == carry["id"]:
                            continue
                        for t in tags[c["good"]]["tags"]:
                            w = TAG_VALUE.get(t)
                            if w:
                                support += w / (1 + seen.get(t, 0))
                                seen[t] = seen.get(t, 0) + 1
                    base = (0.55 + cq) * (1.12 if carry["rarity"] >= 5 else 1.0) * (1 + support)
                    score = base * mult * boxf
                    tid = "+".join(sorted(c["id"] for c in team))
                    if tid not in results or score > results[tid][0]:
                        results[tid] = (score, team, why, missing, tobuild)

    ranked = sorted(results.values(), key=lambda r: -r[0])

    def playable(r):
        return not r[3] and not r[4]

    ranked.sort(key=lambda r: (not playable(r), -r[0]))
    print(f"=== MODE {mode.upper()} · {len(results)} équipes évaluées ===")
    for score, team, why, missing, tobuild in ranked[:6]:
        names = " · ".join(f"{c['name']}({tags[c['good']]['element'][:3]})" for c in team)
        if missing:
            state = "manque: " + ",".join(missing)
        elif tobuild:
            state = "à monter: " + ",".join(tobuild)
        else:
            state = "JOUABLE MAINTENANT"
        print(f"{score:6.2f}  {names}")
        print(f"        {state} | {' · '.join(why) if why else 'aucun bonus de contenu'}")


if __name__ == "__main__":
    main()
