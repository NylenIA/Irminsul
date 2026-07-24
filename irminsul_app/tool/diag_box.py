# Diagnostic QA : etat reel des persos de pool + artefacts equipes.
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
full = json.loads((HERE / "assets/data/characters_full.json").read_text(encoding="utf-8"))
good = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

by_id = {c["id"]: c for c in full["characters"]}
owned = {c["key"]: c for c in good.get("characters", [])}

print("=== persos de pool / alternatives : niveau reel ===")
for cid in ["layla", "diona", "kirara", "thoma", "kachina", "iansan", "xilonen",
            "charlotte", "sigewinne", "jean", "yaemiko", "kujousara", "lisa",
            "kukishinobu", "sucrose", "emilie", "collei", "zhongli", "baizhu",
            "citlali", "sangonomiyakokomi", "barbara"]:
    c = by_id.get(cid)
    if not c:
        print(f"  {cid}: ID INCONNU")
        continue
    oc = owned.get(c["good"])
    print(f"  {c['name']:22s} {'Nv' + str(oc['level']) + ' C' + str(oc['constellation']) if oc else 'NON POSSEDE'}")

print("\n=== artefacts equipes (nb par perso cle) ===")
counts = {}
for a in good.get("artifacts", []):
    loc = a.get("location") or ""
    if loc:
        counts[loc] = counts.get(loc, 0) + 1
for k in ["Beidou", "Yelan", "Xiangling", "Bennett", "Xingqiu", "RaidenShogun",
          "Shenhe", "Barbara", "Sucrose", "Fischl"]:
    print(f"  {k:15s} {counts.get(k, 0)} artefacts | arme:",
          next((w["key"] + " Nv" + str(w["level"])
                for w in good.get("weapons", []) if w.get("location") == k), "aucune"))

print("\n=== niveaux : combien de persos reellement montes ? ===")
lv = [c["level"] for c in good.get("characters", [])]
print(f"  total {len(lv)} | Nv>=90: {sum(1 for x in lv if x >= 90)}"
      f" | Nv>=80: {sum(1 for x in lv if x >= 80)}"
      f" | Nv>=70: {sum(1 for x in lv if x >= 70)}"
      f" | Nv<40: {sum(1 for x in lv if x < 40)}")
