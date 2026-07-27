// Données générées depuis les tables du jeu par
// irminsul_app/tool/gen_gcsim_weapon.py — NE PAS ÉDITER À LA MAIN.
// Lightbearing Moonshard (id 11519)
package lightbearingmoonshard

import (
	"github.com/genshinsim/gcsim/pkg/catalog"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/keys"
	"github.com/genshinsim/gcsim/pkg/model"
)

func init() {
	core.RegisterWeaponFunc(keys.LightbearingMoonshard, NewWeapon)
	catalog.WeaponMap[keys.LightbearingMoonshard] = base
}

var base = &model.WeaponData{
	Id:          11519,
	Key:         "lightbearingmoonshard",
	Rarity:      5,
	WeaponClass: model.WeaponType_WEAPON_SWORD_ONE_HAND,
	ImageName:   "UI_EquipIcon_Sword_SilverwareSaw",
	BaseStats: &model.WeaponStatsData{
			BaseProps: []*model.WeaponProp{
				{
					PropType:     model.FightPropType_FIGHT_PROP_BASE_ATTACK,
					InitialValue: 44.3358,
					Curve:        model.GrowCurveType_GROW_CURVE_ATTACK_304,
				},
				{
					PropType:     model.FightPropType_FIGHT_PROP_CRITICAL_HURT,
					InitialValue: 0.192,
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

