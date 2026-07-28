package zibai

import (
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
)

// C2 « At Birth Are Souls Born, and in Death Leave But Husks »
//   - en mode Lunar Phase Shift, TOUTE l'équipe gagne +30 % de DGT de réaction
//     Lunar-Crystallize ;
//   - au Moonsign « Ascendant Gleam », le passif A1 est renforcé : le 2ᵉ coup
//     de Spirit Steed's Stride gagne 550 % de la DÉF EN PLUS.
//
// C1 : partiellement modélisable seulement. Elle donne 100 de « Phase Shift
// Radiance » et porte à 5 le nombre de chevauchées par mode — or le système
// de Radiance n'est pas simulé (la chevauchée part à chaque compétence chez
// nous), donc cette partie est sans effet ici. Le bonus de DGT sur la
// première chevauchée n'est pas appliqué : sa valeur est tronquée dans les
// données publiques et je ne l'invente pas.

const (
	c2LcrBonus  = 0.30
	c2A1DefMult = 5.5 // 550 % de la DÉF, au Moonsign 2
)

func (c *char) c2() {
	if c.Base.Cons < 2 {
		return
	}
	for _, ch := range c.Core.Player.Chars() {
		ch.AddReactBonusMod(character.ReactBonusMod{
			Base: modifier.NewBase("zibai-c2", -1),
			Amount: func(ai info.AttackInfo) float64 {
				if ai.AttackTag != attacks.AttackTagDirectLunarCrystallize {
					return 0
				}
				if !c.inPhaseShift() {
					return 0
				}
				return c2LcrBonus
			},
		})
	}
}

// c2A1Bonus : renfort du A1 quand l'équipe est en Ascendant Gleam (Moonsign 2).
func (c *char) c2A1Bonus() float64 {
	if c.Base.Cons < 2 || !c.a1Active() {
		return 0
	}
	if c.Core.Player.GetMoonsignLevel() < 2 {
		return 0
	}
	return c2A1DefMult * c.TotalDef(false)
}
