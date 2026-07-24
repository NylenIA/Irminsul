# Ajoute les templates gcsim VALIDES (testes sur GOOD reel) aux equipes.
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
p = HERE / "assets/data/meta_teams.json"
d = json.loads(p.read_text(encoding="utf-8"))

TEMPLATES = {
    "fischl-taser": {
        "chars": ["Fischl", "Beidou", "Xingqiu", "Sucrose"],
        "rotation": (
            "while 1 {\n"
            "    fischl skill;\n"
            "    beidou skill, burst;\n"
            "    xingqiu skill, burst;\n"
            "    sucrose skill;\n"
            "    sucrose attack:6;\n"
            "    fischl burst;\n"
            "    sucrose attack:6;\n"
            "    sucrose skill;\n"
            "    sucrose attack:4;\n"
            "}"
        ),
    },
    "furina-mono": {
        "chars": ["Furina", "Barbara", "Fischl", "Beidou"],
        "rotation": (
            "while 1 {\n"
            "    furina skill;\n"
            "    fischl skill;\n"
            "    beidou skill, burst;\n"
            "    barbara skill;\n"
            "    furina burst;\n"
            "    furina attack:6;\n"
            "    fischl burst;\n"
            "    furina attack:8;\n"
            "}"
        ),
    },
    "raiden-national": {
        "chars": ["Bennett", "Xiangling", "Xingqiu", "RaidenShogun"],
        "rotation": (
            "while 1 {\n"
            "    bennett skill, burst;\n"
            "    xiangling burst, skill;\n"
            "    xingqiu skill, burst;\n"
            "    raiden skill;\n"
            "    raiden burst;\n"
            "    raiden attack:8;\n"
            "    raiden skill;\n"
            "    bennett attack, skill;\n"
            "    xiangling attack, skill;\n"
            "    xingqiu attack:2;\n"
            "}"
        ),
    },
    "nahida-hb": {
        "chars": ["Nahida", "Furina", "Xingqiu", "RaidenShogun"],
        "rotation": (
            "while 1 {\n"
            "    nahida skill, burst;\n"
            "    furina skill;\n"
            "    xingqiu skill, burst;\n"
            "    raiden skill;\n"
            "    raiden attack:10;\n"
            "    nahida skill;\n"
            "    furina attack:2;\n"
            "    xingqiu attack:2;\n"
            "    raiden attack:8;\n"
            "}"
        ),
    },
}

n = 0
for t in d["teams"]:
    tpl = TEMPLATES.get(t["id"])
    if tpl:
        t["gcsim"] = tpl
        n += 1
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {n} templates gcsim ajoutes")
