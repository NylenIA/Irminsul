// Lightbearing Moonshard — signature de Zibai.
//
// Passif « Legacy of Lang-Gan » (valeurs du jeu, R1) :
//   - +20 % de DÉF en permanence ;
//   - +64 % de DGT de réaction Lunar-Crystallize pendant 5 s après que le
//     porteur a utilisé sa compétence élémentaire.
// Barème des raffinements (5★ usuel) : R1 20/64 · R2 25/80 · R3 30/96 ·
// R4 35/112 · R5 40/128.
//
// Statistiques de base, courbe et stat secondaire : voir le fichier généré à
// côté, dérivé des tables du jeu.
package lightbearingmoonshard

import (
	"fmt"

	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/event"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
)

type Weapon struct {
	Index int
}

func (w *Weapon) SetIndex(idx int) { w.Index = idx }
func (w *Weapon) Init() error      { return nil }

const buffKey = "lightbearing-moonshard-lcr"

func NewWeapon(c *core.Core, char *character.CharWrapper, p info.WeaponProfile) (info.Weapon, error) {
	w := &Weapon{}
	r := float64(p.Refine)

	// +20 % DÉF au R1, +5 % par raffinement
	m := make([]float64, attributes.EndStatType)
	m[attributes.DEFP] = 0.15 + 0.05*r
	char.AddStatMod(character.StatMod{
		Base:         modifier.NewBase("lightbearing-def", -1),
		AffectedStat: attributes.DEFP,
		Amount: func() []float64 {
			return m
		},
	})

	// +64 % DGT Lunar-Crystallize pendant 5 s après la compétence
	bonus := 0.48 + 0.16*r
	char.AddReactBonusMod(character.ReactBonusMod{
		Base: modifier.NewBase("lightbearing-lcr", -1),
		Amount: func(ai info.AttackInfo) float64 {
			if ai.AttackTag != attacks.AttackTagDirectLunarCrystallize {
				return 0
			}
			if !char.StatusIsActive(buffKey) {
				return 0
			}
			return bonus
		},
	})

	c.Events.Subscribe(event.OnSkill, func(args ...any) bool {
		if c.Player.ActiveChar().Index() != char.Index() {
			return false
		}
		char.AddStatus(buffKey, 5*60, true)
		return false
	}, fmt.Sprintf("lightbearing-skill-%v", char.Base.Key.String()))

	return w, nil
}
