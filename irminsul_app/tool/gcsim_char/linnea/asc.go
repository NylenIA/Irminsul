package linnea

import (
	"fmt"

	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
	"github.com/genshinsim/gcsim/pkg/reactable"
)

// Passifs de Linnea. Comme pour Zibai, ce sont eux qui comptent.
//
// Innée « Moonsign Benediction : Habitat Survey » : elle aussi convertit les
// Cristallisations Hydro de l'équipe en Lunar-Crystallize, ajoute +0,7 % de
// DGT de base par 100 de SA DÉF (plafond 14 %), et monte le Moonsign d'un
// niveau.
//
// A1 « Field Observation Notes » : tant que Lumi est sur le terrain, les
// ennemis proches ont -15 % de RÉS Geo. Sur une équipe entièrement Geo, c'est
// un gain direct sur tout le monde.
//
// A4 « Universal Naturalist Archive » : elle donne de la maîtrise élémentaire
// à certains alliés, à hauteur de 5 % de sa DÉF, selon le personnage actif.
// La condition exacte (« si le perso actif est … ») est tronquée dans les
// données publiques : j'applique le buff à toute l'équipe et je le signale,
// plutôt que d'inventer une condition.

const (
	a1ResKey    = "linnea-a1-geo-res"
	a1ResShred  = -0.15
	a4EmPerDef  = 0.05
	lcrPerHDef  = 0.007
	lcrDefCapL  = 0.14
)

func (c *char) innate() {
	c.Moonsign = 1
	c.Core.Flags.Custom[reactable.LunarCrystallizeEnableKey] = 1

	c.AddReactBonusMod(character.ReactBonusMod{
		Base: modifier.NewBase("linnea-moonsign-benediction", -1),
		Amount: func(ai info.AttackInfo) float64 {
			if ai.AttackTag != attacks.AttackTagDirectLunarCrystallize {
				return 0
			}
			bonus := c.TotalDef(false) / 100 * lcrPerHDef
			if bonus > lcrDefCapL {
				bonus = lcrDefCapL
			}
			return bonus
		},
	})
}

// a1Shred : appliqué pendant toute la durée de Lumi, depuis skill.go.
func (c *char) a1Shred(dur int) {
	if c.Base.Ascension < 1 {
		return
	}
	enemies := c.Core.Combat.EnemiesWithinArea(
		combat.NewCircleHitOnTarget(c.Core.Combat.Player(), nil, 10), nil)
	for _, e := range enemies {
		e.AddResistMod(info.ResistMod{
			Base:  modifier.NewBaseWithHitlag(a1ResKey, dur),
			Ele:   attributes.Geo,
			Value: a1ResShred,
		})
	}
}

// a4 : maîtrise élémentaire donnée à l'équipe, basée sur sa DÉF.
func (c *char) a4() {
	if c.Base.Ascension < 4 {
		return
	}
	for _, ch := range c.Core.Player.Chars() {
		m := make([]float64, attributes.EndStatType)
		ch.AddStatMod(character.StatMod{
			Base:         modifier.NewBase(fmt.Sprintf("linnea-a4-%v", ch.Base.Key.String()), -1),
			AffectedStat: attributes.EM,
			Amount: func() []float64 {
				m[attributes.EM] = a4EmPerDef * c.TotalDef(false)
				return m
			},
		})
	}
}
