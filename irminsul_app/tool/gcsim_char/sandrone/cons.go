package sandrone

import (
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
)

// C2 « An Heiress Gazed Into the Looking-Glass » : +40 % de DGT CRIT sur les
// faisceaux condensés de l'attaque chargée. Le cumul supplémentaire par
// faisceau tiré est tronqué dans les données publiques — non implémenté.
//
// C1 « Morrow After the Golden Dusk » : ralentit la montée de Decoding Power
// (non modélisé) et donne +30 % de DGT Stellar-Conduct à l'équipe. Ce second
// effet suppose que la réaction existe dans le moteur : voir asc.go et la
// ligne A5 du backlog. Non implémenté pour l'instant.

const c2CritDmgBeam = 0.40

func (c *char) c2() {
	if c.Base.Cons < 2 {
		return
	}
	m := make([]float64, attributes.EndStatType)
	m[attributes.CD] = c2CritDmgBeam
	c.AddAttackMod(character.AttackMod{
		Base: modifier.NewBase("sandrone-c2", -1),
		Amount: func(atk *info.AttackEvent, _ info.Target) []float64 {
			if atk.Info.AttackTag != attacks.AttackTagExtra {
				return nil
			}
			return m
		},
	})
}
