// Données générées depuis les tables du jeu par
// irminsul_app/tool/gen_gcsim_char.py — NE PAS ÉDITER À LA MAIN.
// Multiplicateurs, stats, courbes, ascensions et coût d'ultime sont
// EXACTS. Les frames et les passifs vivent dans les autres fichiers
// et sont approximés (voir commentaires).
package illuga

import (
	"github.com/genshinsim/gcsim/pkg/catalog"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/keys"
	"github.com/genshinsim/gcsim/pkg/model"
)

func init() {
	core.RegisterCharFunc(keys.Illuga, NewChar)
	catalog.CharacterMap[keys.Illuga] = base
}

var base = &model.AvatarData{
	Id:          10000127,
	Key:         "illuga",
	Rarity:      model.QualityType_QUALITY_PURPLE,
	Body:        model.BodyType_BODY_GIRL,
	Region:      model.AssocType_ASSOC_TYPE_NONE,
	Element:     model.ElementType_Rock,
	WeaponClass: model.WeaponType_WEAPON_POLE,
	IconName:    "UI_AvatarIcon_Illuga",
	Stats: &model.AvatarStatsData{
		BaseHp:   1002.9701,
		BaseAtk:  16.0272,
		BaseDef:  68.2122,
		HpCurve:  model.GrowCurveType_GROW_CURVE_HP_S4,
		AtkCurve: model.GrowCurveType_GROW_CURVE_ATTACK_S4,
		DefCruve: model.GrowCurveType_GROW_CURVE_HP_S4,
		PromoData: []*model.PromotionData{
				{
					MaxLevel: 20,
				},
				{
					MaxLevel: 40,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    749.27,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    50.958,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    11.97342,
					},
					},
				},
				{
					MaxLevel: 50,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    1281.6461,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    87.165,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    20.48085,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_ELEMENT_MASTERY,
						Value:    24,
					},
					},
				},
				{
					MaxLevel: 60,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    1991.4808,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    135.441,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    31.82409,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_ELEMENT_MASTERY,
						Value:    48,
					},
					},
				},
				{
					MaxLevel: 70,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    2523.857,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    171.648,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    40.33152,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_ELEMENT_MASTERY,
						Value:    48,
					},
					},
				},
				{
					MaxLevel: 80,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    3056.233,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    207.855,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    48.83895,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_ELEMENT_MASTERY,
						Value:    72,
					},
					},
				},
				{
					MaxLevel: 90,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    3588.6091,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    244.062,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    57.34638,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_ELEMENT_MASTERY,
						Value:    96,
					},
					},
				},
		},
	},
	SkillDetails: &model.AvatarSkillsData{
		Attack:          11271,
		Skill:           11272,
		Burst:           11275,
		BurstEnergyCost: 60.0,
	},
}

var (
	// --- normal : Oathkeeper's Spear
	// 1-Hit DMG (param1)
	normalP1 = []float64{
		0.473662,
		0.512216,
		0.55077,
		0.605847,
		0.644401,
		0.688462,
		0.749047,
		0.809632,
		0.870217,
		0.936309,
		1.0024,
		1.06849,
		1.13459,
		1.20068,
		1.26677,
	}
	// 2-Hit DMG (param2)
	normalP2 = []float64{
		0.485255,
		0.524753,
		0.56425,
		0.620675,
		0.660172,
		0.705313,
		0.76738,
		0.829448,
		0.891515,
		0.959225,
		1.02693,
		1.09465,
		1.16236,
		1.23006,
		1.29777,
	}
	// 3-Hit DMG (param3)
	normalP3 = []float64{
		0.31433,
		0.339915,
		0.3655,
		0.40205,
		0.427635,
		0.456875,
		0.49708,
		0.537285,
		0.57749,
		0.62135,
		0.66521,
		0.70907,
		0.75293,
		0.79679,
		0.84065,
	}
	// 3-Hit DMG (param4)
	normalP4 = []float64{
		0.31433,
		0.339915,
		0.3655,
		0.40205,
		0.427635,
		0.456875,
		0.49708,
		0.537285,
		0.57749,
		0.62135,
		0.66521,
		0.70907,
		0.75293,
		0.79679,
		0.84065,
	}
	// 4-Hit DMG (param5)
	normalP5 = []float64{
		0.762786,
		0.824873,
		0.88696,
		0.975656,
		1.03774,
		1.1087,
		1.20627,
		1.30383,
		1.4014,
		1.50783,
		1.61427,
		1.7207,
		1.82714,
		1.93357,
		2.04001,
	}
	// Charged Attack DMG (param6)
	normalP6 = []float64{
		1.11026,
		1.20063,
		1.291,
		1.4201,
		1.51047,
		1.61375,
		1.75576,
		1.89777,
		2.03978,
		2.1947,
		2.34962,
		2.50454,
		2.65946,
		2.81438,
		2.9693,
	}
	// Charged Attack Stamina Cost (param7)
	normalP7 = []float64{
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
	// Plunge DMG (param8)
	normalP8 = []float64{
		0.639324,
		0.691362,
		0.7434,
		0.81774,
		0.869778,
		0.92925,
		1.01102,
		1.0928,
		1.17457,
		1.26378,
		1.35299,
		1.4422,
		1.5314,
		1.62061,
		1.70982,
	}
	// Low/High Plunge DMG (param9)
	normalP9 = []float64{
		1.27838,
		1.38243,
		1.48649,
		1.63513,
		1.73919,
		1.85811,
		2.02162,
		2.18513,
		2.34865,
		2.52703,
		2.7054,
		2.88378,
		3.06216,
		3.24054,
		3.41892,
	}
	// Low/High Plunge DMG (param10)
	normalP10 = []float64{
		1.59676,
		1.72673,
		1.8567,
		2.04237,
		2.17234,
		2.32088,
		2.52511,
		2.72935,
		2.93359,
		3.15639,
		3.37919,
		3.602,
		3.8248,
		4.04761,
		4.27041,
	}
	// --- skill : Dawnbearing Songbird
	// Press DMG (param1)
	skillP1 = []float64{
		4.8256,
		5.18752,
		5.54944,
		6.032,
		6.39392,
		6.75584,
		7.2384,
		7.72096,
		8.20352,
		8.68608,
		9.16864,
		9.6512,
		10.2544,
		10.8576,
		11.4608,
	}
	// Press DMG (param2)
	skillP2 = []float64{
		2.4128,
		2.59376,
		2.77472,
		3.016,
		3.19696,
		3.37792,
		3.6192,
		3.86048,
		4.10176,
		4.34304,
		4.58432,
		4.8256,
		5.1272,
		5.4288,
		5.7304,
	}
	// Hold DMG (param3)
	skillP3 = []float64{
		6.032,
		6.4844,
		6.9368,
		7.54,
		7.9924,
		8.4448,
		9.048,
		9.6512,
		10.2544,
		10.8576,
		11.4608,
		12.064,
		12.818,
		13.572,
		14.326,
	}
	// Hold DMG (param4)
	skillP4 = []float64{
		3.016,
		3.2422,
		3.4684,
		3.77,
		3.9962,
		4.2224,
		4.524,
		4.8256,
		5.1272,
		5.4288,
		5.7304,
		6.032,
		6.409,
		6.786,
		7.163,
	}
	// CD (param5)
	skillP5 = []float64{
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
	// --- burst : Shadowless Reflection
	// Skill DMG (param1)
	burstP1 = []float64{
		8.272,
		8.8924,
		9.5128,
		10.34,
		10.9604,
		11.5808,
		12.408,
		13.2352,
		14.0624,
		14.8896,
		15.7168,
		16.544,
		17.578,
		18.612,
		19.646,
	}
	// Skill DMG (param2)
	burstP2 = []float64{
		4.136,
		4.4462,
		4.7564,
		5.17,
		5.4802,
		5.7904,
		6.204,
		6.6176,
		7.0312,
		7.4448,
		7.8584,
		8.272,
		8.789,
		9.306,
		9.823,
	}
	// Geo DMG Bonus (param3)
	burstP3 = []float64{
		0.336,
		0.3612,
		0.3864,
		0.42,
		0.4452,
		0.4704,
		0.504,
		0.5376,
		0.5712,
		0.6048,
		0.6384,
		0.672,
		0.714,
		0.756,
		0.798,
	}
	// Lunar-Crystallize Reaction DMG Bonus (param4)
	burstP4 = []float64{
		2.2592,
		2.42864,
		2.59808,
		2.824,
		2.99344,
		3.16288,
		3.3888,
		3.61472,
		3.84064,
		4.06656,
		4.29248,
		4.5184,
		4.8008,
		5.0832,
		5.3656,
	}
	// Nightingale's Song Stacks Gained from Elemental Burst (param5)
	burstP5 = []float64{
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
		21,
	}
	// Nightingale's Song Stacks Gained from Geo Constructs (param6)
	burstP6 = []float64{
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
		5,
	}
	// Duration (param7)
	burstP7 = []float64{
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
		20,
	}
	// CD (param8)
	burstP8 = []float64{
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
	// Energy Cost (param9)
	burstP9 = []float64{
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
