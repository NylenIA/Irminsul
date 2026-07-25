# Diagnostic d'une simulation : ou passe le temps, qui echoue, quelles stats.
# Usage : python tool/diag_sim.py <result.json>
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
st = d["statistics"]
names = [c.get("name") for c in d.get("character_details", [])]


def mean(x):
    return x.get("mean", 0) if isinstance(x, dict) else (x or 0)


print(f"DPS total : {mean(st['dps']):.0f}  (duree {mean(st['duration']):.0f} s)")
print("\n--- DPS / temps de terrain ---")
for i, n in enumerate(names):
    dps = mean(st["character_dps"][i]) if i < len(st["character_dps"]) else 0
    ft = mean(st["field_time"][i]) if i < len(st["field_time"]) else 0
    print(f"  {n:12s} {dps:8.0f} dps | {ft:5.1f} s de terrain")

print("\n--- Actions echouees (moyenne par iteration) ---")
for i, n in enumerate(names):
    if i >= len(st["failed_actions"]):
        continue
    fa = st["failed_actions"][i]
    if not isinstance(fa, dict):
        continue
    parts = [f"{k}={mean(v):.1f}" for k, v in fa.items() if mean(v) > 0.05]
    print(f"  {n:12s} {' '.join(parts) if parts else 'aucune'}")

print("\n--- Stats finales (buffs inclus) ---")
end = st.get("end_stats", [])
labels = ["HP", "HP%", "ATK", "ATK%", "DEF", "DEF%", "EM", "ER", "CR", "CD"]
for i, n in enumerate(names):
    if i >= len(end):
        continue
    row = end[i]
    vals = [mean(x) for x in row[:10]] if isinstance(row, list) else []
    if vals:
        show = ", ".join(f"{lab}={v:.0f}" if lab in ("HP", "ATK", "DEF", "EM")
                         else f"{lab}={v*100:.0f}%"
                         for lab, v in zip(labels, vals))
        print(f"  {n:12s} {show}")
