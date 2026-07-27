"""Génère les fichiers Go d'une ARME absente de gcsim.

Sans l'arme signature, la simulation d'un perso récent échoue
(`invalid weapon …`). Les stats viennent des tables du jeu ; le passif est
écrit à la main à côté quand il est modélisable, sinon signalé comme absent.

    python tool/gen_gcsim_weapon.py "A Teaspoon of Transcendence"
    # -> tool/gcsim_weapon/<clé>/zz_<clé>_gen.go
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datamine  # noqa: E402
from gen_gcsim_char import PROP, promo_go  # noqa: E402

APP = Path(__file__).resolve().parents[1]
OUT = APP / "tool/gcsim_weapon"

CLASS_DIR = {
    "WEAPON_SWORD_ONE_HAND": "sword",
    "WEAPON_CLAYMORE": "claymore",
    "WEAPON_POLE": "polearm",
    "WEAPON_BOW": "bow",
    "WEAPON_CATALYST": "catalyst",
}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    name = sys.argv[1]
    key = re.sub(r"[^a-z0-9]", "", name.lower())

    gdb_path = (datamine.ROOT
                / "data/sources/genshin-db/src/data/English/weapons"
                / f"{key}.json")
    if not gdb_path.exists():
        raise SystemExit(f"arme inconnue de genshin-db : {name}")
    gdb = json.loads(gdb_path.read_text(encoding="utf-8"))
    wid = gdb["id"]

    weapons = {w["id"]: w for w in datamine.load("WeaponExcelConfigData")}
    w = weapons.get(wid)
    if w is None:
        raise SystemExit(f"{name} (id {wid}) absente du datamine")

    promotes = [p for p in datamine.load("WeaponPromoteExcelConfigData")
                if p.get("weaponPromoteId") == w.get("weaponPromoteId")]
    promotes.sort(key=lambda p: p.get("promoteLevel", 0))

    props = []
    for wp in w.get("weaponProp", []):
        t = PROP.get(wp.get("propType"))
        if not t or not wp.get("initValue"):
            continue
        props.append(
            "\t\t\t\t{\n"
            f"\t\t\t\t\tPropType:     model.FightPropType_{t},\n"
            f"\t\t\t\t\tInitialValue: {wp['initValue']:.8g},\n"
            f"\t\t\t\t\tCurve:        model.GrowCurveType_{wp['type']},\n"
            "\t\t\t\t},"
        )

    pretty = "".join(p.capitalize() for p in re.findall(r"[A-Za-z0-9]+", name))
    icon = w.get("icon", f"UI_EquipIcon_{pretty}")
    cls = w["weaponType"]

    lines = [
        "// Données générées depuis les tables du jeu par",
        "// irminsul_app/tool/gen_gcsim_weapon.py — NE PAS ÉDITER À LA MAIN.",
        f"// {name} (id {wid})",
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
        f"\tcore.RegisterWeaponFunc(keys.{pretty}, NewWeapon)",
        f"\tcatalog.WeaponMap[keys.{pretty}] = base",
        "}",
        "",
        "var base = &model.WeaponData{",
        f"\tId:          {wid},",
        f'\tKey:         "{key}",',
        f"\tRarity:      {gdb['rarity']},",
        f"\tWeaponClass: model.WeaponType_{cls},",
        f'\tImageName:   "{icon}",',
        "\tBaseStats: &model.WeaponStatsData{",
        "\t\t\tBaseProps: []*model.WeaponProp{",
        "\n".join(props),
        "\t\t\t},",
        "\t\t\tPromoData: []*model.PromotionData{",
        promo_go(promotes),
        "\t\t\t},",
        "\t},",
        "}",
        "",
    ]

    out_dir = OUT / key
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"zz_{key}_gen.go").write_text("\n".join(lines) + "\n",
                                              encoding="utf-8")
    (out_dir / "_class").write_text(CLASS_DIR[cls], encoding="utf-8")
    # nom Go exact (ATeaspoonOfTranscendence) : l'installeur doit l'utiliser
    # tel quel, sinon la clé ne correspond pas au fichier généré.
    (out_dir / "_ident").write_text(pretty, encoding="utf-8")
    print(f"OK {name} -> tool/gcsim_weapon/{key}/ "
          f"({len(props)} stats, {len(promotes)} paliers, classe {CLASS_DIR[cls]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
