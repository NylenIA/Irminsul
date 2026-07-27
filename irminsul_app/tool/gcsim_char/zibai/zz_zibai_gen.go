// Données générées depuis les tables du jeu par
// irminsul_app/tool/gen_gcsim_char.py — NE PAS ÉDITER À LA MAIN.
// Multiplicateurs, stats, courbes, ascensions et coût d'ultime sont
// EXACTS. Les frames et les passifs vivent dans les autres fichiers
// et sont approximés (voir commentaires).
package zibai

import (
	"github.com/genshinsim/gcsim/pkg/catalog"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/keys"
	"github.com/genshinsim/gcsim/pkg/model"
)

func init() {
	core.RegisterCharFunc(keys.Zibai, NewChar)
	catalog.CharacterMap[keys.Zibai] = base
}

var base = &model.AvatarData{
	Id:          10000126,
	Key:         "zibai",
	Rarity:      model.QualityType_QUALITY_ORANGE,
	Body:        model.BodyType_BODY_GIRL,
	Region:      model.AssocType_ASSOC_TYPE_NONE,
	Element:     model.ElementType_Rock,
	WeaponClass: model.WeaponType_WEAPON_SWORD_ONE_HAND,
	IconName:    "UI_AvatarIcon_Zibai",
	Stats: &model.AvatarStatsData{
		BaseHp:   1005.7526,
		BaseAtk:  17.5028,
		BaseDef:  74.48835,
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
						Value:    862.3419,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    63.8685,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    15.006,
					},
					},
				},
				{
					MaxLevel: 50,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    1475.0585,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    109.2488,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    25.6681,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
						Value:    0.096,
					},
					},
				},
				{
					MaxLevel: 60,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    2292.014,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    169.7558,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    39.8843,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
						Value:    0.192,
					},
					},
				},
				{
					MaxLevel: 70,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    2904.7307,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    215.136,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    50.5464,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
						Value:    0.192,
					},
					},
				},
				{
					MaxLevel: 80,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    3517.4473,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    260.5163,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    61.2086,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
						Value:    0.288,
					},
					},
				},
				{
					MaxLevel: 90,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    4130.164,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    305.8965,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    71.8707,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
						Value:    0.384,
					},
					},
				},
		},
	},
	SkillDetails: &model.AvatarSkillsData{
		Attack:          11261,
		Skill:           11262,
		Burst:           11265,
		BurstEnergyCost: 60.0,
	},
}

var (
	// --- normal : Golden Blade's Petaled Touch
	// 1-Hit DMG (param1)
	normalP1 = []float64{
		0.505542,
		0.546691,
		0.58784,
		0.646624,
		0.687773,
		0.7348,
		0.799462,
		0.864125,
		0.928787,
		0.999328,
		1.06987,
		1.14041,
		1.21095,
		1.28149,
		1.35203,
	}
	// 2-Hit DMG (param2)
	normalP2 = []float64{
		0.465527,
		0.503418,
		0.54131,
		0.595441,
		0.633333,
		0.676638,
		0.736182,
		0.795726,
		0.85527,
		0.920227,
		0.985184,
		1.05014,
		1.1151,
		1.18006,
		1.24501,
	}
	// 3-Hit DMG (param3)
	normalP3 = []float64{
		0.308882,
		0.334023,
		0.359165,
		0.395082,
		0.420223,
		0.448956,
		0.488464,
		0.527973,
		0.567481,
		0.61058,
		0.65368,
		0.69678,
		0.73988,
		0.78298,
		0.826079,
	}
	// 3-Hit DMG (param4)
	normalP4 = []float64{
		0.308882,
		0.334023,
		0.359165,
		0.395082,
		0.420223,
		0.448956,
		0.488464,
		0.527973,
		0.567481,
		0.61058,
		0.65368,
		0.69678,
		0.73988,
		0.78298,
		0.826079,
	}
	// 4-Hit DMG (param5)
	normalP5 = []float64{
		0.778954,
		0.842357,
		0.90576,
		0.996336,
		1.05974,
		1.1322,
		1.23183,
		1.33147,
		1.4311,
		1.53979,
		1.64848,
		1.75717,
		1.86587,
		1.97456,
		2.08325,
	}
	// Charged Attack DMG (param6)
	normalP6 = []float64{
		0.73659,
		0.796545,
		0.8565,
		0.94215,
		1.00211,
		1.07062,
		1.16484,
		1.25906,
		1.35327,
		1.45605,
		1.55883,
		1.66161,
		1.76439,
		1.86717,
		1.96995,
	}
	// Charged Attack DMG (param7)
	normalP7 = []float64{
		0.73659,
		0.796545,
		0.8565,
		0.94215,
		1.00211,
		1.07062,
		1.16484,
		1.25906,
		1.35327,
		1.45605,
		1.55883,
		1.66161,
		1.76439,
		1.86717,
		1.96995,
	}
	// Charged Attack Stamina Cost (param8)
	normalP8 = []float64{
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
	// Plunge DMG (param9)
	normalP9 = []float64{
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
	// Low/High Plunge DMG (param10)
	normalP10 = []float64{
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
	// Low/High Plunge DMG (param11)
	normalP11 = []float64{
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
	// --- skill : Heaven and Earth Made Manifest
	// Lunar Phase Shift 1-Hit DMG (param6)
	skillP6 = []float64{
		0.565792,
		0.608226,
		0.650661,
		0.70724,
		0.749674,
		0.792109,
		0.848688,
		0.905267,
		0.961846,
		1.01843,
		1.075,
		1.13158,
		1.20231,
		1.27303,
		1.34376,
	}
	// Lunar Phase Shift 2-Hit DMG (param7)
	skillP7 = []float64{
		0.521007,
		0.560083,
		0.599158,
		0.651259,
		0.690335,
		0.72941,
		0.781511,
		0.833612,
		0.885712,
		0.937813,
		0.989914,
		1.04201,
		1.10714,
		1.17227,
		1.23739,
	}
	// Lunar Phase Shift 3-Hit DMG (param8)
	skillP8 = []float64{
		0.345694,
		0.371621,
		0.397548,
		0.432117,
		0.458044,
		0.483971,
		0.51854,
		0.55311,
		0.587679,
		0.622248,
		0.656818,
		0.691387,
		0.734599,
		0.777811,
		0.821022,
	}
	// Lunar Phase Shift 3-Hit DMG (param9)
	skillP9 = []float64{
		0.345694,
		0.371621,
		0.397548,
		0.432117,
		0.458044,
		0.483971,
		0.51854,
		0.55311,
		0.587679,
		0.622248,
		0.656818,
		0.691387,
		0.734599,
		0.777811,
		0.821022,
	}
	// Lunar Phase Shift 4-Hit DMG (param10)
	skillP10 = []float64{
		0.871788,
		0.937172,
		1.00256,
		1.08973,
		1.15512,
		1.2205,
		1.30768,
		1.39486,
		1.48204,
		1.56922,
		1.6564,
		1.74358,
		1.85255,
		1.96152,
		2.0705,
	}
	// Lunar Phase Shift Charged Attack DMG (param11)
	skillP11 = []float64{
		0.6595,
		0.708962,
		0.758425,
		0.824375,
		0.873838,
		0.9233,
		0.98925,
		1.0552,
		1.12115,
		1.1871,
		1.25305,
		1.319,
		1.40144,
		1.48388,
		1.56631,
	}
	// Lunar Phase Shift Charged Attack DMG (param12)
	skillP12 = []float64{
		0.6595,
		0.708962,
		0.758425,
		0.824375,
		0.873838,
		0.9233,
		0.98925,
		1.0552,
		1.12115,
		1.1871,
		1.25305,
		1.319,
		1.40144,
		1.48388,
		1.56631,
	}
	// Spirit Steed's Stride 1-Hit DMG (param1)
	skillP1 = []float64{
		1.72528,
		1.85468,
		1.98407,
		2.1566,
		2.286,
		2.41539,
		2.58792,
		2.76045,
		2.93298,
		3.1055,
		3.27803,
		3.45056,
		3.66622,
		3.88188,
		4.09754,
	}
	// Spirit Steed's Stride 2-Hit DMG (param2)
	skillP2 = []float64{
		1.40968,
		1.51541,
		1.62113,
		1.7621,
		1.86783,
		1.97355,
		2.11452,
		2.25549,
		2.39646,
		2.53742,
		2.67839,
		2.81936,
		2.99557,
		3.17178,
		3.34799,
	}
	// Lunar Phase Shift 4-Hit Additional DMG (param3)
	skillP3 = []float64{
		0.29456,
		0.316652,
		0.338744,
		0.3682,
		0.390292,
		0.412384,
		0.44184,
		0.471296,
		0.500752,
		0.530208,
		0.559664,
		0.58912,
		0.62594,
		0.66276,
		0.69958,
	}
	// Lunar Phase Shift Duration (param4)
	skillP4 = []float64{
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
	// --- burst : Tri-Sphere Eminence
	// Skill 1-Hit DMG (param1)
	burstP1 = []float64{
		1.2696,
		1.36482,
		1.46004,
		1.587,
		1.68222,
		1.77744,
		1.9044,
		2.03136,
		2.15832,
		2.28528,
		2.41224,
		2.5392,
		2.6979,
		2.8566,
		3.0153,
	}
	// Skill 2-Hit DMG (param2)
	burstP2 = []float64{
		1.77744,
		1.91075,
		2.04406,
		2.2218,
		2.35511,
		2.48842,
		2.66616,
		2.8439,
		3.02165,
		3.19939,
		3.37714,
		3.55488,
		3.77706,
		3.99924,
		4.22142,
	}
	// CD (param3)
	burstP3 = []float64{
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
	// Energy Cost (param4)
	burstP4 = []float64{
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
