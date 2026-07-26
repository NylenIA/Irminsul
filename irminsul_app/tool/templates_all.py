# Source de VERITE des rotations gcsim des 15 equipes meta.
# Regles : jouables A LA MAIN (pas de perfect-play), jamais d'ulti en tout
# debut de boucle (energie 0 au depart), supports d'abord.
# Chaque template est VALIDE par simulation avant embarquement
# (tool/validate_templates.py).

TEMPLATES = {
    "raiden-national": {
        "chars": ["Bennett", "Xiangling", "Xingqiu", "RaidenShogun"],
        "rotation": """while 1 {
    bennett skill, burst;
    xiangling burst, skill;
    xingqiu skill, burst;
    raiden skill;
    raiden burst;
    raiden attack:8;
    raiden skill;
    bennett attack, skill;
    xiangling attack, skill;
    xingqiu attack:2;
}""",
    },
    "nahida-hb": {
        "chars": ["Nahida", "Furina", "Xingqiu", "RaidenShogun"],
        "rotation": """while 1 {
    nahida skill, burst;
    furina skill;
    xingqiu skill, burst;
    raiden skill;
    raiden attack:10;
    nahida skill;
    furina attack:2;
    xingqiu attack:2;
    raiden attack:8;
}""",
    },
    "fischl-taser": {
        "chars": ["Fischl", "Beidou", "Xingqiu", "Sucrose"],
        "rotation": """while 1 {
    fischl skill;
    beidou skill, burst;
    xingqiu skill, burst;
    sucrose skill;
    sucrose attack:6;
    fischl burst;
    sucrose attack:6;
    sucrose skill;
    sucrose attack:4;
}""",
    },
    "furina-mono": {
        "chars": ["Furina", "Barbara", "Fischl", "Beidou"],
        "rotation": """while 1 {
    furina skill;
    fischl skill;
    beidou skill, burst;
    barbara skill;
    furina burst;
    furina attack:6;
    fischl burst;
    furina attack:8;
}""",
    },
    "mavuika-hc": {
        "chars": ["Mavuika", "Citlali", "Bennett", "Xilonen"],
        "rotation": """while 1 {
    citlali skill;
    xilonen skill;
    bennett skill, burst;
    mavuika skill;
    mavuika burst;
    mavuika charge;
    mavuika charge;
    mavuika charge;
    mavuika charge;
    bennett skill;
    mavuika charge;
    mavuika charge;
}""",
    },
    "mavuika-bis": {
        "chars": ["Mavuika", "Citlali", "Iansan", "Bennett"],
        "rotation": """while 1 {
    iansan skill;
    citlali skill;
    bennett skill, burst;
    mavuika skill;
    mavuika burst;
    mavuika charge;
    mavuika charge;
    mavuika charge;
    mavuika charge;
    bennett skill;
    mavuika charge;
    mavuika charge;
}""",
    },
    "mavuika-onslaught": {
        "chars": ["Mavuika", "Citlali", "Bennett", "Zhongli"],
        "rotation": """while 1 {
    zhongli skill;
    citlali skill;
    bennett skill, burst;
    mavuika skill;
    mavuika burst;
    mavuika charge;
    mavuika charge;
    mavuika charge;
    mavuika charge;
    bennett skill;
    mavuika charge;
    mavuika charge;
}""",
    },
    "neuvillette-hyper": {
        "chars": ["Neuvillette", "Furina", "KaedeharaKazuha", "Baizhu"],
        "rotation": """while 1 {
    furina skill;
    kazuha skill;
    baizhu skill;
    neuvillette skill;
    neuvillette charge;
    furina burst;
    kazuha burst;
    baizhu burst;
    neuvillette charge;
    neuvillette charge;
}""",
    },
    "hutao-double-hydro": {
        "chars": ["HuTao", "Xingqiu", "Yelan", "Zhongli"],
        "rotation": """while 1 {
    yelan skill;
    xingqiu skill, burst;
    yelan burst;
    zhongli skill;
    hutao skill;
    hutao attack:2;
    hutao charge;
    hutao jump;
    hutao attack:2;
    hutao charge;
    hutao jump;
    hutao attack:2;
    hutao charge;
    hutao burst;
}""",
    },
    "ayaka-freeze": {
        "chars": ["KamisatoAyaka", "Shenhe", "SangonomiyaKokomi",
                  "KaedeharaKazuha"],
        "rotation": """while 1 {
    kokomi skill;
    kazuha skill;
    shenhe skill;
    ayaka dash;
    ayaka attack:4;
    shenhe burst;
    kazuha burst;
    ayaka skill;
    ayaka burst;
    ayaka dash;
    ayaka attack:4;
}""",
    },
    "xiao-premium": {
        "chars": ["Xiao", "Faruzan", "Furina", "Xianyun"],
        "rotation": """while 1 {
    furina skill;
    faruzan skill;
    xianyun skill;
    faruzan burst;
    xianyun burst;
    xiao skill;
    xiao burst;
    xiao jump;
    xiao high_plunge;
    xiao jump;
    xiao high_plunge;
    xiao jump;
    xiao high_plunge;
    xiao jump;
    xiao high_plunge;
    xiao jump;
    xiao high_plunge;
    xiao jump;
    xiao high_plunge;
}""",
    },
    "arlecchino-vape": {
        "chars": ["Arlecchino", "Yelan", "Zhongli", "Bennett"],
        "rotation": """while 1 {
    bennett skill;
    yelan skill, burst;
    zhongli skill;
    bennett burst;
    arlecchino skill;
    arlecchino attack:2;
    arlecchino charge;
    arlecchino attack:4;
    arlecchino charge;
    arlecchino attack:4;
}""",
    },
    "nilou-bloom": {
        "chars": ["Nilou", "Nahida", "SangonomiyaKokomi", "Collei"],
        "rotation": """while 1 {
    nahida skill;
    collei skill;
    nilou skill;
    nilou attack:3;
    kokomi skill;
    nahida burst;
    nilou burst;
    kokomi attack:3;
    collei burst;
    nahida attack:2;
}""",
    },
    "skirk-premium": {
        "chars": ["Skirk", "Escoffier", "Citlali", "Furina"],
        "rotation": """while 1 {
    citlali skill;
    furina skill;
    escoffier skill, burst;
    skirk skill;
    skirk attack:5;
    skirk burst;
    skirk attack:5;
    furina burst;
    skirk attack:5;
}""",
    },
    "mualani-vape": {
        "chars": ["Mualani", "Xilonen", "Citlali", "Furina"],
        "rotation": """while 1 {
    citlali skill;
    xilonen skill;
    furina skill;
    mualani skill;
    mualani attack:3;
    mualani skill;
    mualani attack:3;
    furina burst;
    mualani burst;
    mualani skill;
    mualani attack:3;
}""",
    },
}
