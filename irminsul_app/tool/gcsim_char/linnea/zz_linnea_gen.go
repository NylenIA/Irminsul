// Données générées depuis les tables du jeu par
// irminsul_app/tool/gen_gcsim_char.py — NE PAS ÉDITER À LA MAIN.
// Multiplicateurs, stats, courbes, ascensions et coût d'ultime sont
// EXACTS. Les frames et les passifs vivent dans les autres fichiers
// et sont approximés (voir commentaires).
package linnea

import (
	"github.com/genshinsim/gcsim/pkg/catalog"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/keys"
	"github.com/genshinsim/gcsim/pkg/model"
)

func init() {
	core.RegisterCharFunc(keys.Linnea, NewChar)
	catalog.CharacterMap[keys.Linnea] = base
}

var base = &model.AvatarData{
	Id:          10000130,
	Key:         "linnea",
	Rarity:      model.QualityType_QUALITY_ORANGE,
	Body:        model.BodyType_BODY_GIRL,
	Region:      model.AssocType_ASSOC_TYPE_NONE,
	Element:     model.ElementType_Rock,
	WeaponClass: model.WeaponType_WEAPON_BOW,
	IconName:    "UI_AvatarIcon_Linnea",
	Stats: &model.AvatarStatsData{
		BaseHp:   770.28253,
		BaseAtk:  11.172,
		BaseDef:  70.5994,
		HpCurve:  model.GrowCurveType_GROW_CURVE_HP_S5,
		AtkCurve: model.GrowCurveType_GROW_CURVE_ATTACK_S5,
		DefCruve: model.GrowCurveType_GROW_CURVE_HP_S5,
		PromoData: []*model.PromotionData{
				{
					MaxLevel: 20,
				},
				{
					MaxLevel: 40,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    660.44763,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    60.534,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    9.57828,
					},
					},
				},
				{
					MaxLevel: 50,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    1129.7131,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    103.545,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    16.3839,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL,
						Value:    0.048,
					},
					},
				},
				{
					MaxLevel: 60,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    1755.4003,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    160.893,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    25.45806,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL,
						Value:    0.096,
					},
					},
				},
				{
					MaxLevel: 70,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    2224.6658,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    203.904,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    32.26368,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL,
						Value:    0.096,
					},
					},
				},
				{
					MaxLevel: 80,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    2693.9312,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    246.915,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    39.0693,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL,
						Value:    0.144,
					},
					},
				},
				{
					MaxLevel: 90,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    3163.1965,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    289.926,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    45.87492,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL,
						Value:    0.192,
					},
					},
				},
		},
	},
	SkillDetails: &model.AvatarSkillsData{
		Attack:          11301,
		Skill:           11302,
		Burst:           11305,
		BurstEnergyCost: 60.0,
	},
}

var (
	// --- normal : Capture Protocol
	// 1-Hit DMG (param1)
	normalP1 = []float64{
		0.589969,
		0.637989,
		0.68601,
		0.754611,
		0.802632,
		0.857513,
		0.932974,
		1.00843,
		1.0839,
		1.16622,
		1.24854,
		1.33086,
		1.41318,
		1.4955,
		1.57782,
	}
	// 2-Hit DMG (param2)
	normalP2 = []float64{
		0.511519,
		0.553155,
		0.59479,
		0.654269,
		0.695904,
		0.743488,
		0.808914,
		0.874341,
		0.939768,
		1.01114,
		1.08252,
		1.15389,
		1.22527,
		1.29664,
		1.36802,
	}
	// 3-Hit DMG (param3)
	normalP3 = []float64{
		0.816312,
		0.882756,
		0.9492,
		1.04412,
		1.11056,
		1.1865,
		1.29091,
		1.39532,
		1.49974,
		1.61364,
		1.72754,
		1.84145,
		1.95535,
		2.06926,
		2.18316,
	}
	// Aimed Shot (param4)
	normalP4 = []float64{
		0.4386,
		0.4743,
		0.51,
		0.561,
		0.5967,
		0.6375,
		0.6936,
		0.7497,
		0.8058,
		0.867,
		0.9282,
		0.9894,
		1.0506,
		1.1118,
		1.173,
	}
	// Fully-Charged Aimed Shot (param5)
	normalP5 = []float64{
		1.24,
		1.333,
		1.426,
		1.55,
		1.643,
		1.736,
		1.86,
		1.984,
		2.108,
		2.232,
		2.356,
		2.48,
		2.635,
		2.79,
		2.945,
	}
	// Plunge DMG (param6)
	normalP6 = []float64{
		0.568288,
		0.614544,
		0.6608,
		0.72688,
		0.773136,
		0.826,
		0.898688,
		0.971376,
		1.04406,
		1.12336,
		1.20266,
		1.28195,
		1.36125,
		1.44054,
		1.51984,
	}
	// Low/High Plunge DMG (param7)
	normalP7 = []float64{
		1.13634,
		1.22883,
		1.32132,
		1.45345,
		1.54594,
		1.65165,
		1.79699,
		1.94234,
		2.08769,
		2.24624,
		2.4048,
		2.56336,
		2.72192,
		2.88048,
		3.03904,
	}
	// Low/High Plunge DMG (param8)
	normalP8 = []float64{
		1.41934,
		1.53487,
		1.6504,
		1.81544,
		1.93097,
		2.063,
		2.24454,
		2.42609,
		2.60763,
		2.80568,
		3.00373,
		3.20178,
		3.39982,
		3.59787,
		3.79592,
	}
	// --- skill : Countermeasure: Lumi's Battle Cry!
	// Lumi Pound-Pound Pummeler DMG (param1)
	skillP1 = []float64{
		0.96,
		1.032,
		1.104,
		1.2,
		1.272,
		1.344,
		1.44,
		1.536,
		1.632,
		1.728,
		1.824,
		1.92,
		2.04,
		2.16,
		2.28,
	}
	// Lumi Heavy Overdrive Hammer DMG (param2)
	skillP2 = []float64{
		1,
		1.075,
		1.15,
		1.25,
		1.325,
		1.4,
		1.5,
		1.6,
		1.7,
		1.8,
		1.9,
		2,
		2.125,
		2.25,
		2.375,
	}
	// Lumi Million Ton Crush DMG (param3)
	skillP3 = []float64{
		4,
		4.3,
		4.6,
		5,
		5.3,
		5.6,
		6,
		6.4,
		6.8,
		7.2,
		7.6,
		8,
		8.5,
		9,
		9.5,
	}
	// Lumi Duration (param4)
	skillP4 = []float64{
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
		25,
	}
	// CD (param5)
	skillP5 = []float64{
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
		18,
	}
	// --- burst : Memo: Survival Guide in Extreme Conditions
	// Initial Healing Amount (param1)
	burstP1 = []float64{
		770.375,
		847.424,
		930.893,
		1020.78,
		1117.09,
		1219.82,
		1328.98,
		1444.55,
		1566.54,
		1694.95,
		1829.79,
		1971.04,
		2118.72,
		2272.82,
		2433.33,
	}
	// Initial Healing Amount (param2)
	burstP2 = []float64{
		1.6,
		1.72,
		1.84,
		2,
		2.12,
		2.24,
		2.4,
		2.56,
		2.72,
		2.88,
		3.04,
		3.2,
		3.4,
		3.6,
		3.8,
	}
	// Continuous Healing (param3)
	burstP3 = []float64{
		154.075,
		169.485,
		186.179,
		204.156,
		223.419,
		243.965,
		265.795,
		288.91,
		313.308,
		338.991,
		365.958,
		394.209,
		423.744,
		454.563,
		486.667,
	}
	// Continuous Healing (param4)
	burstP4 = []float64{
		0.32,
		0.344,
		0.368,
		0.4,
		0.424,
		0.448,
		0.48,
		0.512,
		0.544,
		0.576,
		0.608,
		0.64,
		0.68,
		0.72,
		0.76,
	}
	// Healing Duration (param5)
	burstP5 = []float64{
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
		12,
	}
	// CD (param6)
	burstP6 = []float64{
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
		15,
	}
	// Energy Cost (param7)
	burstP7 = []float64{
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
		60,
	}
)
