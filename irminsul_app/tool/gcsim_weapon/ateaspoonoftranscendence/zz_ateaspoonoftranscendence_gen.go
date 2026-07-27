// Données générées depuis les tables du jeu par
// irminsul_app/tool/gen_gcsim_weapon.py — NE PAS ÉDITER À LA MAIN.
// A Teaspoon of Transcendence (id 12516)
package ateaspoonoftranscendence

import (
	"github.com/genshinsim/gcsim/pkg/catalog"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/keys"
	"github.com/genshinsim/gcsim/pkg/model"
)

func init() {
	core.RegisterWeaponFunc(keys.ATeaspoonOfTranscendence, NewWeapon)
	catalog.WeaponMap[keys.ATeaspoonOfTranscendence] = base
}

var base = &model.WeaponData{
	Id:          12516,
	Key:         "ateaspoonoftranscendence",
	Rarity:      5,
	WeaponClass: model.WeaponType_WEAPON_CLAYMORE,
	ImageName:   "UI_EquipIcon_Claymore_CrystallineSword",
	BaseStats: &model.WeaponStatsData{
			BaseProps: []*model.WeaponProp{
				{
					PropType:     model.FightPropType_FIGHT_PROP_BASE_ATTACK,
					InitialValue: 47.537,
					Curve:        model.GrowCurveType_GROW_CURVE_ATTACK_302,
				},
				{
					PropType:     model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
					InitialValue: 0.096,
					Curve:        model.GrowCurveType_GROW_CURVE_CRITICAL_301,
				},
			},
			PromoData: []*model.PromotionData{
				{
					MaxLevel: 20,
				},
				{
					MaxLevel: 40,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    31.1,
					},
					},
				},
				{
					MaxLevel: 50,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    62.2,
					},
					},
				},
				{
					MaxLevel: 60,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    93.4,
					},
					},
				},
				{
					MaxLevel: 70,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    124.5,
					},
					},
				},
				{
					MaxLevel: 80,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    155.6,
					},
					},
				},
				{
					MaxLevel: 90,
					AddProps: []*model.PromotionAddProp{
					{
						PropType: model.FightPropType_FIGHT_PROP_BASE_ATTACK,
						Value:    186.7,
					},
					},
				},
			},
	},
}

