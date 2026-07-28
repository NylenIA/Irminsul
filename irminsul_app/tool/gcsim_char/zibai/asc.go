package zibai

import (
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
	"github.com/genshinsim/gcsim/pkg/reactable"
)

// Les passifs de Zibai SONT son moteur de dégâts. Sans eux, elle ne fait que
// ses coups directs — c'est ce qui expliquait un écart énorme avec le jeu.
//
// Innée « Moonsign Benediction : The Coursing Sun and Moon »
//   - convertit toute réaction Cristallisation Hydro de l'équipe en
//     Lunar-Crystallize (drapeau moteur) ;
//   - chaque 100 DÉF de Zibai augmente les DGT de base de Lunar-Crystallize
//     de 0,7 %, plafonné à 14 % ;
//   - fait monter le Moonsign de l'équipe d'un niveau (avec un second porteur
//     de Moonsign, l'équipe passe en « Ascendant Gleam »).
//
// A1 « The Selenic Adeptus Descends » : le 2ᵉ coup de Spirit Steed's Stride
// gagne 60 % de la DÉF de Zibai pendant 4 s après la compétence.
//
// A4 « Layered Peaks Pierce the Clouds » : chaque autre allié Geo donne
// +15 % de DÉF à Zibai, chaque allié Hydro +60 de maîtrise élémentaire.

const (
	a1Key         = "zibai-selenic-descent"
	lcrDefPerStep = 0.007 // 0,7 % par tranche de 100 DÉF
	lcrDefCap     = 0.14  // plafond 14 %
	a1DefBonus    = 0.6
	a4DefPerGeo   = 0.15
	a4EmPerHydro  = 60.0
)

// innate : Moonsign, conversion des cristallisations, bonus de DGT de base.
func (c *char) innate() {
	c.Moonsign = 1
	c.Core.Flags.Custom[reactable.LunarCrystallizeEnableKey] = 1

	c.AddReactBonusMod(character.ReactBonusMod{
		Base: modifier.NewBase("zibai-moonsign-benediction", -1),
		Amount: func(ai info.AttackInfo) float64 {
			if ai.AttackTag != attacks.AttackTagDirectLunarCrystallize {
				return 0
			}
			bonus := c.TotalDef(false) / 100 * lcrDefPerStep
			if bonus > lcrDefCap {
				bonus = lcrDefCap
			}
			return bonus
		},
	})
}

// a4 : la composition de l'équipe fait sa DÉF et sa maîtrise.
func (c *char) a4() {
	if c.Base.Ascension < 4 {
		return
	}
	geo, hydro := 0, 0
	for _, x := range c.Core.Player.Chars() {
		if x.Index() == c.Index() {
			continue
		}
		switch x.Base.Element {
		case attributes.Geo:
			geo++
		case attributes.Hydro:
			hydro++
		}
	}
	m := make([]float64, attributes.EndStatType)
	m[attributes.DEFP] = a4DefPerGeo * float64(geo)
	m[attributes.EM] = a4EmPerHydro * float64(hydro)
	c.AddStatMod(character.StatMod{
		Base:         modifier.NewBase("zibai-a4", -1),
		AffectedStat: attributes.NoStat,
		Amount: func() []float64 {
			return m
		},
	})
}

// a1 : bonus sur le 2ᵉ coup de la chevauchée, appliqué dans skill.go.
func (c *char) a1Active() bool {
	return c.Base.Ascension >= 1 && c.StatusIsActive(a1Key)
}

func (c *char) a1Bonus() float64 {
	if !c.a1Active() {
		return 0
	}
	return a1DefBonus * c.TotalDef(false)
}
