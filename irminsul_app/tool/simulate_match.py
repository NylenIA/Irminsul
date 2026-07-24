# QA : simule le matcher Dart (team_matcher.dart) en Python contre un GOOD reel.
# Doit refleter EXACTEMENT la logique Dart (choix du mieux monte, ER, equipement).
# Usage : python tool/simulate_match.py <chemin_GOOD.json>
import json
import sys
from pathlib import Path

BUILT = 70  # kBuiltLevel

HERE = Path(__file__).resolve().parents[1]
full = json.loads((HERE / "assets/data/characters_full.json").read_text(encoding="utf-8"))
teams = json.loads((HERE / "assets/data/meta_teams.json").read_text(encoding="utf-8"))
er_weapons = json.loads((HERE / "assets/data/weapons_er.json").read_text(encoding="utf-8"))
good = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

by_id = {c["id"]: c for c in full["characters"]}
owned = {c["key"]: c for c in good.get("characters", [])}

er = {k: 100.0 for k in owned}
art_count = {k: 0 for k in owned}
wkey, wlvl = {}, {}
for a in good.get("artifacts", []):
    loc = a.get("location") or ""
    if loc not in er:
        continue
    art_count[loc] += 1
    if a.get("mainStatKey") == "enerRech_":
        r5 = a.get("rarity", 5) >= 5
        mx, mlvl = (51.8, 20) if r5 else (38.9, 16)
        er[loc] += mx * (min(a.get("level", 0), mlvl) / mlvl)
    for s in a.get("substats", []):
        if s.get("key") == "enerRech_":
            er[loc] += s.get("value", 0) or 0
for w in good.get("weapons", []):
    loc = w.get("location") or ""
    if loc not in er:
        continue
    wkey[loc], wlvl[loc] = w.get("key", ""), int(w.get("level", 1))
    table = er_weapons.get(w.get("key", ""))
    if table:
        lvl = max(1, min(int(w.get("level", 1)), len(table)))
        er[loc] += table[lvl - 1]


def best_of(ids):
    """Mieux monte d'abord (priorite meta), sinon plus haut niveau."""
    cands = []
    for rank, cid in enumerate(ids):
        c = by_id.get(cid)
        o = owned.get(c["good"]) if c else None
        if c and o:
            cands.append((c, o, rank))
    if not cands:
        return None
    cands.sort(key=lambda x: (0 if x[1]["level"] >= BUILT else 1,
                             x[2] if x[1]["level"] >= BUILT else -x[1]["level"],
                             x[2]))
    return cands[0]


results = []
for t in teams["teams"]:
    if not t.get("slots"):
        continue
    rows, miss, warn, equip = [], [], [], []
    ready = True
    for s in t["slots"]:
        tit = by_id.get(s["id"])
        if tit is None:
            rows.append(f"!! id inconnu {s['id']}")
            continue
        chosen, oc, via = tit, owned.get(tit["good"]), ""
        if oc is None:
            alt = best_of(s["alts"])
            if alt:
                chosen, oc, via = alt[0], alt[1], " (ALT)"
        if oc is None:
            ready = False
            sug = best_of(s["pool"])
            if sug:
                tag = " A-MONTER" if sug[1]["level"] < BUILT else ""
                miss.append(f"{tit['name']} -> en attendant: {sug[0]['name']}"
                            f" (C{sug[1]['constellation']} Nv{sug[1]['level']}{tag})")
            else:
                miss.append(f"{tit['name']} -> aucun remplacant")
            rows.append(f"[MANQUE] {tit['name']}")
            continue
        key = chosen["good"]
        low = oc["level"] < BUILT
        if low:
            ready = False
        no_art = art_count.get(key, 0) == 0
        weak_w = (not low) and (wlvl.get(key, 0) <= 20)
        e, req = er.get(key), s.get("er")
        tags = ""
        if low:
            tags += " A-MONTER"
        if no_art:
            equip.append(f"{chosen['name']}: aucun artefact equipe")
            tags += " SANS-ARTEFACTS"
        elif req and e is not None and e + 3 < req:
            warn.append(f"{chosen['name']} {e:.0f}%<{req}%")
            tags += f" ER!{e:.0f}<{req}"
        if weak_w:
            equip.append(f"{chosen['name']}: arme {wkey.get(key,'?')} Nv{wlvl.get(key,0)}")
            tags += " ARME-FAIBLE"
        rows.append(f"{chosen['name']}{via} C{oc['constellation']} Nv{oc['level']}{tags}")
    results.append((ready, not miss, len(miss), -t["dps"], t["name"], t["mode"],
                    rows, miss, warn, equip))

results.sort(key=lambda x: (not x[0], not x[1], x[2], x[3]))
for ready, complete, nmiss, _, name, mode, rows, miss, warn, equip in results:
    tag = "PRETE" if ready else ("COMPLETE" if complete else f"MANQUE {nmiss}")
    print(f"\n[{tag}] {name} ({mode})")
    for r in rows:
        print("   ", r)
    for m in miss:
        print("    *", m)
    for w in warn:
        print("    ! ER:", w)
    for e in equip:
        print("    ! EQUIP:", e)
