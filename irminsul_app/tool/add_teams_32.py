# Étape 3.2 : ajoute 10 équipes méta standards (ids vérifiés) à meta_teams.json.
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
full = json.loads((HERE / "assets/data/characters_full.json").read_text(encoding="utf-8"))
ids = {c["id"] for c in full["characters"]}
p = HERE / "assets/data/meta_teams.json"
d = json.loads(p.read_text(encoding="utf-8"))
existing = {t["id"] for t in d["teams"]}


def S(i, alts=None, er=None, role="", pool=None):
    return {"id": i, "alts": alts or [], "er": er, "role": role, "pool": pool or []}


new = [
    {"id": "neuvillette-hyper", "mode": "abyss", "name": "Neuvillette Hypercarry",
     "half": "1ʳᵉ moitié", "badge": "meta", "dps": 205000, "rotation": "~18 s",
     "note": "mono-cible & AoE", "missing": None,
     "slots": [
         S("neuvillette", role="DPS principal (attaque chargée)"),
         S("furina", er=180, role="Buff + Hydro off-field"),
         S("kaedeharakazuha", role="Swirl + buff Hydro", pool=["sucrose"]),
         S("baizhu", alts=["zhongli"], role="Bouclier + soin", pool=["layla", "thoma"]),
     ],
     "rotationSteps": ["Furina E", "Kazuha E → Q (absorbe Hydro)", "Baizhu E → Q",
                       "Neuvillette attaque chargée (draine les gouttes)"],
     "combos": "Neuvillette se soigne via ses gouttes : ne l'interromps pas pendant la charge. Kazuha doit absorber Hydro (tourbillonne après le E de Furina)."},

    {"id": "raiden-national", "mode": "abyss", "name": "Raiden National",
     "half": "2ᵉ moitié", "badge": "meta", "dps": 190000, "rotation": "~24 s",
     "note": "la valeur sûre depuis des années", "missing": None,
     "slots": [
         S("raidenshogun", er=200, role="DPS burst + batterie"),
         S("xiangling", er=230, role="Pyro off-field (Pyronado)"),
         S("xingqiu", alts=["yelan"], er=200, role="Hydro off-field"),
         S("bennett", er=190, role="Soin + buff ATK"),
     ],
     "rotationSteps": ["Bennett E → Q", "Xiangling Guoba → Q", "Xingqiu E → Q",
                       "Raiden E → Q, enchaîne pendant son ultime"],
     "combos": "Fais tourner l'énergie : les E de Bennett/Raiden rechargent Xiangling. Le Q de Raiden rembourse toute l'équipe."},

    {"id": "hutao-double-hydro", "mode": "abyss", "name": "Hu Tao Double Hydro",
     "half": "1ʳᵉ moitié", "badge": "meta", "dps": 195000, "rotation": "~20 s",
     "note": "vaporisation en continu", "missing": None,
     "slots": [
         S("hutao", role="DPS principal (vapo)"),
         S("xingqiu", er=200, role="Hydro off-field"),
         S("yelan", er=170, role="Hydro off-field + buff"),
         S("zhongli", alts=["citlali"], role="Bouclier (confort N2C)", pool=["layla", "thoma"]),
     ],
     "rotationSteps": ["Yelan E → Q", "Xingqiu E → Q", "Zhongli E (bouclier)",
                       "Hu Tao E puis N2C ×8-9, Q en fin de fenêtre"],
     "combos": "Le combo : 2 attaques normales → attaque chargée → annule la reculade (N2C jump/dash cancel). Sous 50 % PV pour son passif si tu maîtrises."},

    {"id": "ayaka-freeze", "mode": "abyss", "name": "Ayaka Freeze",
     "half": "2ᵉ moitié", "badge": "viable", "dps": 175000, "rotation": "~21 s",
     "note": "contrôle total par le gel", "missing": None,
     "slots": [
         S("kamisatoayaka", role="DPS principal"),
         S("shenhe", er=160, role="Buff Cryo (Plumes)"),
         S("sangonomiyakokomi", alts=["barbara"], role="Hydro + soin (gel)"),
         S("kaedeharakazuha", role="Swirl + regroupement", pool=["sucrose"]),
     ],
     "rotationSteps": ["Kokomi E", "Kazuha E → Q (absorbe Cryo)", "Shenhe E → Q",
                       "Ayaka sprint (infusion) → attaques → Q sur les ennemis gelés"],
     "combos": "Alterne Hydro/Cryo pour un gel permanent. L'ultime d'Ayaka doit partir sur des ennemis gelés et regroupés par Kazuha."},

    {"id": "xiao-premium", "mode": "abyss", "name": "Xiao Hyper (Xianyun)",
     "half": "1ʳᵉ moitié", "badge": "meta", "dps": 185000, "rotation": "~22 s",
     "note": "pluie de piqués", "missing": None,
     "slots": [
         S("xiao", role="DPS principal (piqués)"),
         S("faruzan", er=200, role="Buff Anémo + shred"),
         S("furina", er=180, role="Buff universel"),
         S("xianyun", er=155, role="Boost de piqués + soin"),
     ],
     "rotationSteps": ["Furina E", "Faruzan E → Q", "Xianyun E → Q",
                       "Xiao Q, enchaîne les attaques plongeantes"],
     "combos": "Plonge DANS le vortex de Faruzan. Xianyun augmente la hauteur des piqués et soigne — aucun temps mort."},

    {"id": "arlecchino-vape", "mode": "onslaught", "name": "Arlecchino Vaporisation",
     "half": "Boss unique", "badge": "meta", "dps": 200000, "rotation": "~25 s",
     "note": "burst massif sur boss", "missing": None,
     "slots": [
         S("arlecchino", role="DPS principal (Directives)"),
         S("yelan", alts=["xingqiu"], er=170, role="Hydro off-field"),
         S("zhongli", alts=["citlali"], role="Bouclier", pool=["layla", "thoma"]),
         S("bennett", er=190, role="Soin + buff (elle ne se soigne pas seule)"),
     ],
     "rotationSteps": ["Bennett E → Q", "Yelan E → Q", "Zhongli E",
                       "Arlecchino E (marque) → attaques chargées → récolte les Directives"],
     "combos": "Arlecchino ne peut pas être soignée par les autres (sauf son Q) : le buff de Bennett compte, pas son soin. Marque TOUS les ennemis avant de frapper."},

    {"id": "nilou-bloom", "mode": "theater", "name": "Nilou Bloom",
     "half": "Acte Dendro/Hydro", "badge": "viable", "dps": 160000, "rotation": "~19 s",
     "note": "explosions de Cœurs de rosée", "missing": None,
     "slots": [
         S("nilou", role="Moteur de Cœurs de rosée"),
         S("nahida", role="Application Dendro"),
         S("sangonomiyakokomi", alts=["barbara"], role="Hydro + soin (dégâts Bloom subis)"),
         S("collei", role="2ᵉ Dendro", pool=["emilie"]),
     ],
     "rotationSteps": ["Nahida E → Q", "Nilou E (danse) → 3 coups", "Kokomi E",
                       "Collei E, entretiens les réactions"],
     "combos": "⚠ Uniquement des persos Dendro et Hydro, sinon Nilou perd son passif. Les Cœurs blessent aussi ton équipe : garde Kokomi active."},

    {"id": "skirk-premium", "mode": "abyss", "name": "Skirk Premium",
     "half": "1ʳᵉ moitié", "badge": "meta", "dps": 230000, "rotation": "~20 s",
     "note": "le plafond Cryo actuel", "missing": None,
     "slots": [
         S("skirk", role="DPS principal (Sept-Phases)"),
         S("escoffier", role="Shred Cryo/Hydro + soin"),
         S("citlali", er=150, role="Buff + bouclier", pool=["layla", "diona"]),
         S("furina", er=180, role="Buff universel"),
     ],
     "rotationSteps": ["Citlali E", "Escoffier E → Q", "Furina E",
                       "Skirk E, enchaîne et ramasse les fissures du Néant"],
     "combos": "Skirk n'utilise pas d'énergie : maximise sa fenêtre de terrain. Ramasse les fissures générées par tes Cryo/Hydro pour renforcer son ultime."},

    {"id": "mualani-vape", "mode": "onslaught", "name": "Mualani Vaporisation",
     "half": "Boss unique", "badge": "viable", "dps": 175000, "rotation": "~18 s",
     "note": "morsures requin mono-cible", "missing": None,
     "slots": [
         S("mualani", role="DPS Nightsoul (morsures)"),
         S("xilonen", role="Shred + buff"),
         S("citlali", er=150, role="Buff Cryo + bouclier", pool=["layla", "diona"]),
         S("furina", er=180, role="Buff universel"),
     ],
     "rotationSteps": ["Citlali E", "Xilonen E", "Furina E",
                       "Mualani E (surf) → morsure chargée ×3"],
     "combos": "Chaque 3ᵉ morsure est énorme. Surfe entre les phases pour recharger les points Nightsoul ; surtout du mono-cible."},

    {"id": "fischl-taser", "mode": "theater", "name": "Taser Électro-charge",
     "half": "Acte flexible", "badge": "viable", "dps": 150000, "rotation": "~18 s",
     "note": "très flexible, zéro 5★ requis", "missing": None,
     "slots": [
         S("fischl", role="Électro off-field (Oz)"),
         S("beidou", er=200, role="Électro off-field (parade)"),
         S("xingqiu", alts=["yelan"], er=200, role="Hydro off-field"),
         S("sucrose", alts=["kaedeharakazuha"], role="Swirl + regroupement + EM"),
     ],
     "rotationSteps": ["Fischl E (Oz)", "Beidou E (parade) → Q", "Xingqiu E → Q",
                       "Sucrose E et attaques, pilote et tourbillonne"],
     "combos": "Tout tourne tout seul : garde Oz et les éclairs de Beidou actifs. Sucrose partage sa Maîtrise via son passif."},
]

for t in new:
    assert t["id"] not in existing, f"doublon: {t['id']}"
    for s in t["slots"]:
        assert s["id"] in ids, f"id inconnu: {s['id']}"
        for a in s["alts"] + s["pool"]:
            assert a in ids, f"alt/pool inconnu: {a}"

by = {c["id"]: c for c in full["characters"]}
for t in new:
    chars = []
    for s in t["slots"]:
        c = by[s["id"]]
        name = c["name"]
        short = name.split(" ")[-1] if len(name) > 12 else name
        chars.append({"n": short, "e": c["element"],
                      "i": c["icon"].replace("UI_AvatarIcon_", "")})
    t["chars"] = chars

d["teams"].extend(new)
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {len(new)} equipes ajoutees -> total {len(d['teams'])}")
