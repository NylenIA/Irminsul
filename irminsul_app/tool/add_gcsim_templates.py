# Injecte les rotations gcsim VALIDEES (tool/validate_templates.py, 15/15 OK)
# et les CONTENUS ACTUELS du cycle dans meta_teams.json.
import json
from pathlib import Path

from templates_all import TEMPLATES

HERE = Path(__file__).resolve().parents[1]
p = HERE / "assets/data/meta_teams.json"
d = json.loads(p.read_text(encoding="utf-8"))

n = 0
for t in d["teams"]:
    tpl = TEMPLATES.get(t["id"])
    if tpl:
        t["gcsim"] = {"chars": tpl["chars"], "rotation": tpl["rotation"]}
        n += 1

# Contenus ACTUELS du patch (sources publiques datees ; maj via synchro OTA).
d["content"] = {
    "updated": "2026-07-25",
    "abyss": {
        "cycle": "16 juillet – 15 août 2026",
        "blessing": ("Lune des glaces déferlantes : les DGT Cryo infligés par "
                     "attaque chargée déclenchent une onde de choc (DGT "
                     "réels) sur la cible."),
        "floor12": ("Étage 12 · 1ʳᵉ moitié : Supraconducteur +200 %, "
                    "Stellar-Conduct +75 % · 2ᵉ moitié : Électro-chargé "
                    "+200 %, Lunar-Charged +75 %."),
        "strategy": ("Le cycle amplifie massivement Cryo/Électro : "
                     "Supraconducteur, Stellar-Conduct et Lunar-Charged. "
                     "Tes équipes Électro (Flins/Columbina, Taser) et "
                     "Hyperbloom sont favorisées ; une team Cryo à attaques "
                     "chargées profite à fond de la bénédiction."),
    },
    "theater": {
        "cycle": "saison du 1ᵉʳ août 2026",
        "elements": "Cryo · Hydro · Électro",
        "opening": ("Ouverture : Yelan, Aino, Flins, Ororon, Skirk, Layla · "
                    "invités : Arlecchino, Chevreuse, Kazuha, Tighnari"),
        "strategy": ("Prépare la LARGEUR Cryo/Hydro/Électro : plusieurs "
                     "supports montés de ces éléments. Taser et les noyaux "
                     "Hydro/Électro s'adaptent très bien ; profite des "
                     "invités (Arlecchino, Kazuha) pour les actes durs."),
    },
    "onslaught": {
        "cycle": "8 juillet – 11 août 2026",
        "bosses": ("① Ombre de la Matrice de source secrète · ② Seigneur des "
                   "Profondeurs cachées · ③ Automate de source secrète"),
        "strategy": ("3 équipes SANS partage de personnages : "
                     "① Cryo/Électro (Supraconducteur ou Stellar-Conduct) · "
                     "② réactions Lunaires (Lunar-Charged / Bloom / "
                     "Crystallize) · ③ team Nightsoul menée par Natlan — ta "
                     "Mavuika est taillée pour la 3ᵉ arène."),
    },
}

p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {n} templates gcsim + contenus du cycle injectes")
