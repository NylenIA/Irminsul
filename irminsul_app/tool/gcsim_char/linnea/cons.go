package linnea

import (
	"fmt"

	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
)

// C2 « Tidings of Joy and Sorrow » : dans les 8 s qui suivent un Moondrift
// Harmony, tous les alliés Hydro et Geo gagnent +40 % de DGT CRIT.
//
// « Moondrift Harmony » est un déclencheur lié aux réactions lunaires qui
// n'est pas exposé tel quel par le moteur. Je l'accroche donc à SA COMPÉTENCE,
// qui est le moment où le joueur déclenche l'effet en pratique. C'est une
// approximation, elle est écrite ici : sur une équipe qui enchaîne les
// réactions, le buff serait en réalité plus souvent actif.
//
// C1 « Provisional Classification » : cumuls « Field Catalog » (6 par
// compétence, max 18) dont l'effet est tronqué dans les données publiques —
// NON implémenté.

const (
	c2Key     = "linnea-c2-critdmg"
	c2CritDmg = 0.40
	c2Dur     = 8 * 60
)

func (c *char) c2(dur int) {
	if c.Base.Cons < 2 {
		return
	}
	for _, ch := range c.Core.Player.Chars() {
		if ch.Base.Element != attributes.Hydro && ch.Base.Element != attributes.Geo {
			continue
		}
		m := make([]float64, attributes.EndStatType)
		m[attributes.CD] = c2CritDmg
		ch.AddStatMod(character.StatMod{
			Base:         modifier.NewBaseWithHitlag(fmt.Sprintf("%v-%v", c2Key, ch.Base.Key.String()), dur),
			AffectedStat: attributes.CD,
			Amount: func() []float64 {
				return m
			},
		})
	}
}
