# Met a jour assets/data/meta_teams.json — la BDD lue par l'app (et par la
# synchro OTA). A relancer a chaque cycle : les CONTENUS ci-dessous sont
# verifies sur sources publiques et dates, jamais devines.
#
#   python tool/validate_templates.py <gcsim.exe> --json tool/ref_dps_synth.json
#   python tool/update_meta_db.py
#
# Ordre impose : on ne publie une rotation qu'apres 16/16 OK en simulation.
import json
from pathlib import Path

from templates_all import TEMPLATES

HERE = Path(__file__).resolve().parents[1]
TOOL = Path(__file__).resolve().parent

# --- CONTENUS ACTUELS -------------------------------------------------------
# Sources verifiees le 2026-07-27 (voir champ "source" de chaque mode).
# from/to en ISO : l'app en deduit « en cours / a venir / termine », elle ne
# fait pas confiance a une phrase figee.
CONTENT = {
    "updated": "2026-07-27",
    "abyss": {
        "from": "2026-07-16",
        "to": "2026-08-15",
        "cycle": "16 juillet – 15 août 2026",
        "blessing": (
            "Lune des glaces déferlantes : quand le personnage actif inflige "
            "des DGT Cryo avec une attaque chargée, une onde de choc de DGT "
            "réels frappe la cible."
        ),
        "floor12": (
            "Étage 12 · 1ʳᵉ moitié : DGT Supraconducteur +200 %, "
            "Stellar-Conduct +75 % · 2ᵉ moitié : DGT Électro-chargé +200 %, "
            "Lunar-Charged +75 %."
        ),
        "strategy": (
            "1ʳᵉ moitié : Cryo/Électro pour le Supraconducteur — garde un "
            "Électro pour la salle 1 (Rejeton de la nuit glacée). 2ᵉ moitié : "
            "il te FAUT de l'Électro-chargé en salle 3 (l'Idole Pipilpan n'est "
            "vulnérable qu'à cette réaction) : prévois Hydro + Électro. La "
            "bénédiction récompense en plus une équipe Cryo à attaques "
            "chargées."
        ),
        "source": "Game8 — Spiral Abyss 6.7 (vérifié le 27/07/2026)",
        # Regles LUES PAR L'OPTIMISEUR (pas seulement du texte) : ce sont
        # elles qui font qu'une equipe « colle » au contenu du moment.
        "boostedReactions": {
            "superconduct": 2.0, "stellar-conduct": 0.75,
            "electro-charged": 2.0, "lunar-charged": 0.75,
        },
        "requiredElements": ["electro"],
        "favoredTags": [],
    },
    "theater": {
        "from": "2026-07-01",
        "to": "2026-07-30",
        "cycle": "Saison 25 · 1ᵉʳ – 30 juillet 2026",
        "elements": "Pyro · Cryo · Électro",
        "allowedElements": ["pyro", "cryo", "electro"],
        "guests": ["Columbina", "Kinich", "Yumemizuki Mizuki", "Jahoda"],
        "opening": (
            "Ouverture imposée : Arlecchino, Cyno, Ganyu, Bennett, Beidou, "
            "Diona · Invités : Columbina, Kinich, Mizuki, Jahoda · Boss : "
            "Terreur jadeplume (acte 3), Primo-vishap Géo (acte 6), Landrover "
            "super-lourd (acte 8), Drake Aeonblight (acte 10)"
        ),
        "strategy": (
            "Hors invités, SEULS Pyro, Cryo et Électro sont jouables : monte "
            "de la largeur dans ces trois éléments (Surcharge Pyro/Électro et "
            "un noyau Cryo). Les équipes Hydro/Dendro sont interdites ce "
            "mois-ci — l'app les masque au lieu de te les proposer. La saison "
            "se termine le 30/07 ; la suivante arrivera par la synchro."
        ),
        "source": (
            "Game8 — Théâtre imaginaire 6.7 / Saison 25 + Genshin Impact Wiki "
            "(vérifié le 27/07/2026)"
        ),
        # Actes longs, pas de bonus de reaction : ce qui compte est de tenir
        # la distance (soin/bouclier) avec seulement 3 elements autorises.
        "boostedReactions": {},
        "requiredElements": [],
        "favoredTags": ["heal", "shield"],
    },
    "onslaught": {
        "from": "2026-07-08",
        "to": "2026-08-11",
        "cycle": "8 juillet – 11 août 2026",
        "bosses": (
            "① Matrice de source secrète du Réseau du Superviseur : Volonté "
            "de la Ruche · ② Seigneur des Profondeurs cachées : Murmureur de "
            "cauchemars · ③ Automate de source secrète : Dispositif de "
            "configuration"
        ),
        "strategy": (
            "① détruis vite les 4 drones Hydro (Cryo, Hydro, Dendro ou Pyro) "
            "sinon le boss se protège d'un bouclier · ② casse le Bouclier des "
            "profondeurs en 15 s : les réactions Lunaires lui infligent "
            "+300 % de DGT (Lunar-Charged / Lunar-Bloom) · ③ détruis les "
            "piliers avec des personnages Nightsoul (déclenchés à 15 s au "
            "lieu de 40) avant l'AoE fatale — ta Mavuika est taillée pour "
            "cette arène. À partir de la difficulté 4 (Menaçant), aucun "
            "personnage ne peut servir dans deux arènes."
        ),
        "source": (
            "Game8 — Stygian Onslaught 6.7 + GamingOnPhone (vérifié le "
            "27/07/2026)"
        ),
        # Boss ② : le bouclier prend +300 % des reactions Lunaires.
        # Boss ③ : les piliers ne tombent vite qu'avec du Nightsoul.
        # Boss unique => bouclier/soin evitent les interruptions.
        "boostedReactions": {"lunar-charged": 3.0, "lunar-bloom": 3.0},
        "requiredElements": [],
        "favoredTags": ["nightsoul", "shield", "heal"],
    },
}

# --- MODES ------------------------------------------------------------------
# Une equipe peut servir plusieurs contenus. Le filtre de saison du Theatre
# retire de lui-meme celles dont un element est interdit ce mois-ci.
MODES = {
    "mavuika-bis": ["abyss", "theater"],
    "mavuika-hc": ["abyss", "theater"],
    "chevreuse-overload": ["abyss", "theater"],
    "ayaka-freeze": ["abyss", "theater"],
}

# --- EQUIPES AJOUTEES -------------------------------------------------------
# Rotation validee par simulation (voir templates_all.py + ref_dps_synth.json).
NEW_TEAMS = [
    {
        "id": "chevreuse-overload",
        "mode": "abyss",
        "name": "Surcharge Chevreuse — Xiangling · Bennett · Fischl",
        "half": "Pyro/Électro pur",
        "badge": "meta",
        "dps": 0,  # rempli par ref_dps_synth.json
        "note": "F2P, et légale quand le Théâtre interdit Hydro/Dendro",
        "chars": [
            {"n": "Chevreuse", "e": "pyro", "i": "Chevreuse"},
            {"n": "Xiangling", "e": "pyro", "i": "Xiangling"},
            {"n": "Bennett", "e": "pyro", "i": "Bennett"},
            {"n": "Fischl", "e": "electro", "i": "Fischl"},
        ],
        "missing": None,
        "slots": [
            {"id": "chevreuse", "alts": [], "er": 200,
             "role": "Buff ATK/RÉS + soin (Surcharge)", "pool": []},
            {"id": "xiangling", "alts": [], "er": 200,
             "role": "DPS Pyro hors terrain", "pool": ["dehya"]},
            {"id": "bennett", "alts": [], "er": 190,
             "role": "Soin + buff ATK", "pool": []},
            {"id": "fischl", "alts": [], "er": 130,
             "role": "Application Électro hors terrain",
             "pool": ["beidou", "lisa", "dori"]},
        ],
        "combos": (
            "Chevreuse n'accepte QUE du Pyro/Électro : chaque Surcharge "
            "déclenchée rend de la vie et convertit sa RÉS en ATK pour toute "
            "l'équipe. Fischl entretient l'Électro, Xiangling le Pyro."
        ),
        "rotationSteps": [
            "Fischl E",
            "Xiangling E → Q",
            "Bennett E → Q",
            "Chevreuse E → Q",
            "Attaques normales de Chevreuse (Surcharges à répétition)",
        ],
        "rotation": "~21 s",
    },
]


def main():
    p = HERE / "assets/data/meta_teams.json"
    d = json.loads(p.read_text(encoding="utf-8"))

    # 1) equipes ajoutees (idempotent : on remplace si l'id existe deja)
    by_id = {t["id"]: t for t in d["teams"]}
    for team in NEW_TEAMS:
        if team["id"] in by_id:
            by_id[team["id"]].update(team)
        else:
            d["teams"].append(dict(team))

    # 2) rotations gcsim validees
    n_tpl = 0
    for t in d["teams"]:
        tpl = TEMPLATES.get(t["id"])
        if tpl:
            t["gcsim"] = {"chars": tpl["chars"], "rotation": tpl["rotation"]}
            n_tpl += 1

    # 3) modes multiples
    for t in d["teams"]:
        t["modes"] = MODES.get(t["id"], [t["mode"]])

    # 4) DPS de reference : meme box standard pour toutes → comparable.
    ref_path = TOOL / "ref_dps_synth.json"
    n_dps = 0
    if ref_path.exists():
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
        for t in d["teams"]:
            r = ref.get(t["id"])
            if r:
                t["dps"] = r["dps"]
                n_dps += 1
        d["dpsRef"] = "synth-standard"

    # 5) contenus du cycle
    d["content"] = CONTENT
    d["dataKind"] = "CURATED"

    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    print(f"OK {len(d['teams'])} equipes · {n_tpl} rotations gcsim · "
          f"{n_dps} DPS de reference · contenus {CONTENT['updated']}")


if __name__ == "__main__":
    main()
