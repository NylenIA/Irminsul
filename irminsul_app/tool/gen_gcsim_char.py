"""Génère le fichier de DONNÉES Go d'un perso absent de gcsim.

Ce que ce script produit est 100 % dérivé des tables du jeu (voir
tool/datamine.py) : multiplicateurs par niveau de talent, stats de base,
courbes de croissance, paliers d'ascension, coût d'ultime, CD. Rien n'est
inventé ici. Le KIT (frames, mécaniques, passifs) est écrit à la main à côté,
et ses approximations sont signalées dans le code.

    python tool/gen_gcsim_char.py Sandrone
    # -> tool/gcsim_char/sandrone/zz_sandrone_gen.go

Le fichier généré contient :
  - les tableaux de multiplicateurs (attack/charge/plunge/skill/burst)
  - l'entrée catalogue (stats + ascensions) injectée dans catalog.CharacterMap
  - l'enregistrement core.RegisterCharFunc(keys.<Perso>, NewChar)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datamine  # noqa: E402

APP = Path(__file__).resolve().parents[1]
OUT = APP / "tool/gcsim_char"

# datamine -> enums Go de gcsim
QUALITY = {"QUALITY_ORANGE": "QUALITY_ORANGE", "QUALITY_PURPLE": "QUALITY_PURPLE",
           "QUALITY_ORANGE_SP": "QUALITY_ORANGE_SP"}
WEAPON = {
    "WEAPON_SWORD_ONE_HAND": "WEAPON_SWORD_ONE_HAND",
    "WEAPON_CLAYMORE": "WEAPON_CLAYMORE",
    "WEAPON_POLE": "WEAPON_POLE",
    "WEAPON_BOW": "WEAPON_BOW",
    "WEAPON_CATALYST": "WEAPON_CATALYST",
}
ELEMENT = {  # nom genshin-db -> enum gcsim
    "ELEMENT_PYRO": "Fire", "ELEMENT_HYDRO": "Water", "ELEMENT_ELECTRO": "Electric",
    "ELEMENT_CRYO": "Ice", "ELEMENT_ANEMO": "Wind", "ELEMENT_GEO": "Rock",
    "ELEMENT_DENDRO": "Grass",
}
PROP = {
    "FIGHT_PROP_BASE_HP": "FIGHT_PROP_BASE_HP",
    "FIGHT_PROP_BASE_ATTACK": "FIGHT_PROP_BASE_ATTACK",
    "FIGHT_PROP_BASE_DEFENSE": "FIGHT_PROP_BASE_DEFENSE",
    "FIGHT_PROP_CRITICAL": "FIGHT_PROP_CRITICAL",
    "FIGHT_PROP_CRITICAL_HURT": "FIGHT_PROP_CRITICAL_HURT",
    "FIGHT_PROP_ATTACK_PERCENT": "FIGHT_PROP_ATTACK_PERCENT",
    "FIGHT_PROP_HP_PERCENT": "FIGHT_PROP_HP_PERCENT",
    "FIGHT_PROP_DEFENSE_PERCENT": "FIGHT_PROP_DEFENSE_PERCENT",
    "FIGHT_PROP_ELEMENT_MASTERY": "FIGHT_PROP_ELEMENT_MASTERY",
    "FIGHT_PROP_CHARGE_EFFICIENCY": "FIGHT_PROP_CHARGE_EFFICIENCY",
    "FIGHT_PROP_HEAL_ADD": "FIGHT_PROP_HEAL_ADD",
    "FIGHT_PROP_FIRE_ADD_HURT": "FIGHT_PROP_FIRE_ADD_HURT",
    "FIGHT_PROP_WATER_ADD_HURT": "FIGHT_PROP_WATER_ADD_HURT",
    "FIGHT_PROP_ELEC_ADD_HURT": "FIGHT_PROP_ELEC_ADD_HURT",
    "FIGHT_PROP_ICE_ADD_HURT": "FIGHT_PROP_ICE_ADD_HURT",
    "FIGHT_PROP_WIND_ADD_HURT": "FIGHT_PROP_WIND_ADD_HURT",
    "FIGHT_PROP_ROCK_ADD_HURT": "FIGHT_PROP_ROCK_ADD_HURT",
    "FIGHT_PROP_GRASS_ADD_HURT": "FIGHT_PROP_GRASS_ADD_HURT",
    "FIGHT_PROP_PHYSICAL_ADD_HURT": "FIGHT_PROP_PHYSICAL_ADD_HURT",
}


def go_floats(values: list[float], indent: str = "\t\t") -> str:
    return "\n".join(f"{indent}{v:.6g}," for v in values)


def param_series(talent: dict, index: int) -> list[float]:
    """Valeur du paramètre `index` pour les 15 niveaux de talent."""
    out = []
    for lvl in talent["params"]:
        out.append(lvl[index] if index < len(lvl) else 0.0)
    return out


def promo_go(promotes: list[dict]) -> str:
    """Paliers d'ascension au format model.PromotionData."""
    blocks = []
    for p in promotes:
        props = []
        for ap in p.get("addProps", []):
            t = PROP.get(ap.get("propType"))
            v = ap.get("value")
            if not t or not v:
                continue
            props.append(
                "\t\t\t\t\t{\n"
                f"\t\t\t\t\t\tPropType: model.FightPropType_{t},\n"
                f"\t\t\t\t\t\tValue:    {v:.8g},\n"
                "\t\t\t\t\t},"
            )
        body = f"\t\t\t\t\tMaxLevel: {p.get('unlockMaxLevel', 20)},\n"
        if props:
            body += "\t\t\t\t\tAddProps: []*model.PromotionAddProp{\n" \
                    + "\n".join(props) + "\n\t\t\t\t\t},\n"
        blocks.append("\t\t\t\t{\n" + body + "\t\t\t\t},")
    return "\n".join(blocks)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    name = sys.argv[1]
    d = datamine.extract(name)
    key = name.lower()
    pretty = name

    gdb = json.loads(
        (datamine.ROOT / "data/sources/genshin-db/src/data/English/characters"
         / f"{key}.json").read_text(encoding="utf-8"))
    element = ELEMENT[gdb["elementType"]]
    weapon = WEAPON[gdb["weaponType"]]
    quality = QUALITY[gdb["rarity"] == 5 and "QUALITY_ORANGE" or "QUALITY_PURPLE"]

    promotes = [p for p in datamine.load("AvatarPromoteExcelConfigData")
                if p.get("avatarPromoteId") == d["promoteId"]]
    promotes.sort(key=lambda p: p.get("promoteLevel", 0))

    normal = d["talents"]["normal"]
    skill = d["talents"]["skill"]
    burst = d["talents"]["burst"]
    curves = {c["type"]: c["growCurve"] for c in d["growCurves"]}

    lines = [
        "// Données générées depuis les tables du jeu par",
        "// irminsul_app/tool/gen_gcsim_char.py — NE PAS ÉDITER À LA MAIN.",
        "// Multiplicateurs, stats, courbes, ascensions et coût d'ultime sont",
        "// EXACTS. Les frames et les passifs vivent dans les autres fichiers",
        "// et sont approximés (voir commentaires).",
        f"package {key}",
        "",
        "import (",
        '\t"github.com/genshinsim/gcsim/pkg/catalog"',
        '\t"github.com/genshinsim/gcsim/pkg/core"',
        '\t"github.com/genshinsim/gcsim/pkg/core/keys"',
        '\t"github.com/genshinsim/gcsim/pkg/model"',
        ")",
        "",
        "func init() {",
        f"\tcore.RegisterCharFunc(keys.{pretty}, NewChar)",
        f"\tcatalog.CharacterMap[keys.{pretty}] = base",
        "}",
        "",
        "var base = &model.AvatarData{",
        f"\tId:          {d['avatarId']},",
        f'\tKey:         "{key}",',
        f"\tRarity:      model.QualityType_{quality},",
        "\tBody:        model.BodyType_BODY_GIRL,",
        "\tRegion:      model.AssocType_ASSOC_TYPE_NONE,",
        f"\tElement:     model.ElementType_{element},",
        f"\tWeaponClass: model.WeaponType_{weapon},",
        f'\tIconName:    "UI_AvatarIcon_{pretty}",',
        "\tStats: &model.AvatarStatsData{",
        f"\t\tBaseHp:   {d['baseHp']:.8g},",
        f"\t\tBaseAtk:  {d['baseAtk']:.8g},",
        f"\t\tBaseDef:  {d['baseDef']:.8g},",
        f"\t\tHpCurve:  model.GrowCurveType_{curves.get('FIGHT_PROP_BASE_HP', 'GROW_CURVE_HP_S5')},",
        f"\t\tAtkCurve: model.GrowCurveType_{curves.get('FIGHT_PROP_BASE_ATTACK', 'GROW_CURVE_ATTACK_S5')},",
        f"\t\tDefCruve: model.GrowCurveType_{curves.get('FIGHT_PROP_BASE_DEFENSE', 'GROW_CURVE_HP_S5')},",
        "\t\tPromoData: []*model.PromotionData{",
        promo_go(promotes),
        "\t\t},",
        "\t},",
        "\tSkillDetails: &model.AvatarSkillsData{",
        f"\t\tAttack:          {normal['skillId']},",
        f"\t\tSkill:           {skill['skillId']},",
        f"\t\tBurst:           {burst['skillId']},",
        f"\t\tBurstEnergyCost: {burst['energy']:.1f},",
        "\t},",
        "}",
        "",
    ]

    # tableaux de multiplicateurs, nommés selon les libellés genshin-db
    talents = json.loads(
        (datamine.ROOT / "data/sources/genshin-db/src/data/English/talents"
         / f"{key}.json").read_text(encoding="utf-8"))
    lines.append("var (")
    for role, combat in (("normal", "combat1"), ("skill", "combat2"),
                         ("burst", "combat3")):
        labels = talents[combat]["attributes"]["labels"]
        t = d["talents"][role]
        lines.append(f"\t// --- {role} : {talents[combat]['name']}")
        # IMPORTANT : on nomme chaque tableau d'après le NUMÉRO DE PARAMÈTRE
        # cité dans le libellé ({param6}), pas d'après la position du libellé.
        # Les deux diffèrent (Zibai : le libellé n°1 du mode lunaire pointe
        # vers param6) et confondre les deux ferait jouer les mauvais chiffres.
        seen: set[int] = set()
        for lab in labels:
            title = lab.split("|")[0]
            for num in sorted({int(n) for n in
                               re.findall(r"\{param(\d+)", lab)}):
                if num in seen:
                    continue
                seen.add(num)
                series = param_series(t, num - 1)
                if not any(series):
                    continue
                lines.append(f"\t// {title} (param{num})")
                lines.append(f"\t{role}P{num} = []float64{{")
                lines.append(go_floats(series))
                lines.append("\t}")
    lines.append(")")

    out_dir = OUT / key
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"zz_{key}_gen.go"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK {pretty} -> {p.relative_to(APP)} "
          f"({len(promotes)} paliers, ultime {burst['energy']} énergie)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
