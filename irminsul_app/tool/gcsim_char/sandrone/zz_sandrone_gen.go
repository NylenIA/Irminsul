// Données générées depuis les tables du jeu par
// irminsul_app/tool/gen_gcsim_char.py — NE PAS ÉDITER À LA MAIN.
// Multiplicateurs, stats, courbes, ascensions et coût d'ultime sont
// EXACTS. Les frames et les passifs vivent dans les autres fichiers
// et sont approximés (voir commentaires).
package sandrone

import (
	"github.com/genshinsim/gcsim/pkg/catalog"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/keys"
	"github.com/genshinsim/gcsim/pkg/model"
)

func init() {
	core.RegisterCharFunc(keys.Sandrone, NewChar)
	catalog.CharacterMap[keys.Sandrone] = base
}

var base = &model.AvatarData{
	Id:          10000133,
	Key:         "sandrone",
	Rarity:      model.QualityType_QUALITY_ORANGE,
	Body:        model.BodyType_BODY_GIRL,
	Region:      model.AssocType_ASSOC_TYPE_NONE,
	Element:     model.ElementType_Ice,
	WeaponClass: model.WeaponType_WEAPON_CLAYMORE,
	IconName:    "UI_AvatarIcon_Sandrone",
	Stats: &model.AvatarStatsData{
		BaseHp:   1029.5856,
		BaseAtk:  26.6266,
		BaseDef:  58.57357,
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
						Value:    882.77655,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    50.2227,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    22.828234,
					},
					},
				},
				{
					MaxLevel: 50,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_HP,
						Value:    1510.0126,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    85.90725,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    39.048294,
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
						Value:    2346.3271,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    133.48665,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    60.67504,
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
						Value:    2973.5632,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    169.1712,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    76.8951,
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
						Value:    3600.799,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    204.85574,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    93.115166,
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
						Value:    4228.035,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_DEFENSE,
						Value:    240.5403,
					},
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    109.33523,
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
		Attack:          11331,
		Skill:           11332,
		Burst:           11335,
		BurstEnergyCost: 60.0,
	},
}

var (
	// --- normal : Formule Phenomenale: Self-Evident Proposition
	// 1-Hit DMG (param1)
	normalP1 = []float64{
		0.762863,
		0.824957,
		0.88705,
		0.975755,
		1.03785,
		1.10881,
		1.20639,
		1.30396,
		1.40154,
		1.50798,
		1.61443,
		1.72088,
		1.82732,
		1.93377,
		2.04021,
	}
	// 2-Hit DMG (param2)
	normalP2 = []float64{
		0.67197,
		0.726665,
		0.78136,
		0.859496,
		0.914191,
		0.9767,
		1.06265,
		1.1486,
		1.23455,
		1.32831,
		1.42207,
		1.51584,
		1.6096,
		1.70337,
		1.79713,
	}
	// 3-Hit DMG (param3)
	normalP3 = []float64{
		1.02804,
		1.11171,
		1.19539,
		1.31493,
		1.39861,
		1.49424,
		1.62573,
		1.75722,
		1.88872,
		2.03216,
		2.17561,
		2.31906,
		2.4625,
		2.60595,
		2.7494,
	}
	// Charged Attack Sweeping Fire DMG (param4)
	normalP4 = []float64{
		0.43,
		0.465,
		0.5,
		0.55,
		0.585,
		0.625,
		0.68,
		0.735,
		0.79,
		0.85,
		0.91,
		0.97,
		1.03,
		1.09,
		1.15,
	}
	// Charged Attack Condensed Beam DMG (param5)
	normalP5 = []float64{
		1.2255,
		1.32525,
		1.425,
		1.5675,
		1.66725,
		1.78125,
		1.938,
		2.09475,
		2.2515,
		2.4225,
		2.5935,
		2.7645,
		2.9355,
		3.1065,
		3.2775,
	}
	// Charged Attack Condensed Beam Stellar-Conduct DMG (param6)
	normalP6 = []float64{
		0.817,
		0.8835,
		0.95,
		1.045,
		1.1115,
		1.1875,
		1.292,
		1.3965,
		1.501,
		1.615,
		1.729,
		1.843,
		1.957,
		2.071,
		2.185,
	}
	// DMG When in Power Overdrive (param7)
	normalP7 = []float64{
		0.43,
		0.465,
		0.5,
		0.55,
		0.585,
		0.625,
		0.68,
		0.735,
		0.79,
		0.85,
		0.91,
		0.97,
		1.03,
		1.09,
		1.15,
	}
	// Plunge DMG (param8)
	normalP8 = []float64{
		0.745878,
		0.806589,
		0.8673,
		0.95403,
		1.01474,
		1.08413,
		1.17953,
		1.27493,
		1.37033,
		1.47441,
		1.57849,
		1.68256,
		1.78664,
		1.89071,
		1.99479,
	}
	// Low/High Plunge DMG (param9)
	normalP9 = []float64{
		1.49144,
		1.61284,
		1.73423,
		1.90766,
		2.02905,
		2.16779,
		2.35856,
		2.54932,
		2.74009,
		2.9482,
		3.1563,
		3.36441,
		3.57252,
		3.78063,
		3.98874,
	}
	// Low/High Plunge DMG (param10)
	normalP10 = []float64{
		1.86289,
		2.01452,
		2.16615,
		2.38277,
		2.5344,
		2.70769,
		2.94596,
		3.18424,
		3.42252,
		3.68246,
		3.94239,
		4.20233,
		4.46227,
		4.72221,
		4.98215,
	}
	// --- skill : Formule Phenomenale: Differential Analysis
	// Prism Shot DMG (param1)
	skillP1 = []float64{
		0.324,
		0.3483,
		0.3726,
		0.405,
		0.4293,
		0.4536,
		0.486,
		0.5184,
		0.5508,
		0.5832,
		0.6156,
		0.648,
		0.6885,
		0.729,
		0.7695,
	}
	// Prism Shot Stellar-Conduct DMG (param2)
	skillP2 = []float64{
		0.216,
		0.2322,
		0.2484,
		0.27,
		0.2862,
		0.3024,
		0.324,
		0.3456,
		0.3672,
		0.3888,
		0.4104,
		0.432,
		0.459,
		0.486,
		0.513,
	}
	// CD (param3)
	skillP3 = []float64{
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
		4,
	}
	// --- burst : Formule Phenomenale: Q.E.D.
	// Bombardment DMG (param1)
	burstP1 = []float64{
		0.88216,
		0.948322,
		1.01448,
		1.1027,
		1.16886,
		1.23502,
		1.32324,
		1.41146,
		1.49967,
		1.58789,
		1.6761,
		1.76432,
		1.87459,
		1.98486,
		2.09513,
	}
	// Convective Inhibition Ray DMG (param2)
	burstP2 = []float64{
		3.308,
		3.5561,
		3.8042,
		4.135,
		4.3831,
		4.6312,
		4.962,
		5.2928,
		5.6236,
		5.9544,
		6.2852,
		6.616,
		7.0295,
		7.443,
		7.8565,
	}
	// Convective Inhibition Ray Stellar-Conduct DMG (param3)
	burstP3 = []float64{
		2.20533,
		2.37073,
		2.53613,
		2.75667,
		2.92207,
		3.08747,
		3.308,
		3.52853,
		3.74907,
		3.9696,
		4.19013,
		4.41067,
		4.68633,
		4.962,
		5.23767,
	}
	// CD (param4)
	burstP4 = []float64{
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
	// Energy Cost (param5)
	burstP5 = []float64{
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
