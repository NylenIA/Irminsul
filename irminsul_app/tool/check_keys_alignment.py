# Verifie l'insertion d'iansan dans pkg/core/keys/character.dm.go :
# voisinage hutao/ineffa correct dans les TROIS regions (const, noms, valeurs)
# et assertion de taille relative intacte. Sort 1 si suspect.
import re
import sys
from pathlib import Path

t = (Path(sys.argv[1]) / "pkg/core/keys/character.dm.go").read_text(
    encoding="utf-8")
ok = True

# 1) region const (lignes avec commentaire // nom)
consts = re.findall(r"^\t(\w+) +// ([a-z0-9]*)$", t, re.M)
cnames = [c[1] for c in consts]
if "iansan" not in cnames:
    print("!! const iansan absent")
    ok = False
else:
    i = cnames.index("iansan")
    if cnames[i - 1] != "hutao" or cnames[i + 1] != "ineffa":
        print(f"!! voisinage const: {cnames[i-1]} / {cnames[i+1]}")
        ok = False

# 2) region noms
names = re.findall(r'^\t"([a-z0-9]+)",$', t, re.M)
if "iansan" not in names:
    print("!! nom iansan absent")
    ok = False
else:
    i = names.index("iansan")
    if names[i - 1] != "hutao" or names[i + 1] != "ineffa":
        print(f"!! voisinage noms: {names[i-1]} / {names[i+1]}")
        ok = False

# 3) region valeurs (identifiants)
vals = re.findall(r"^\t([A-Za-z0-9]+),$", t, re.M)
if "Iansan" not in vals:
    print("!! valeur Iansan absente")
    ok = False
else:
    i = vals.index("Iansan")
    if vals[i - 1] != "HuTao" or vals[i + 1] != "Ineffa":
        print(f"!! voisinage valeurs: {vals[i-1]} / {vals[i+1]}")
        ok = False

# 4) assertion relative presente (compte auto-coherent via iota)
if "int(InvalidChar+1)-len(_CharNames)" not in t.replace(" ", ""):
    print("note: assertion de taille non trouvee (structure changee ?)")

print("alignement OK" if ok else "alignement KO")
sys.exit(0 if ok else 1)
