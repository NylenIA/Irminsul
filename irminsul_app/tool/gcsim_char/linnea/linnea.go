// Linnea — troisième pièce de la meilleure équipe de Zibai selon KQM
// (Zibai — Illuga — Linnea — Columbina). Absente de gcsim jusqu'ici.
//
// EXACT (tables du jeu) : multiplicateurs de son invocation « Lumi »
// (scaling DÉF), durées, CD, valeurs de soin, coût d'ultime.
//
// APPROXIMÉ, écrit dans le code : frames, particules (3), cadence des coups
// de Lumi (répartie sur la durée), passifs et constellations non implémentés.
package linnea

import (
	tmpl "github.com/genshinsim/gcsim/internal/template/character"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
)

type char struct {
	*tmpl.Character
}

func NewChar(s *core.Core, w *character.CharWrapper, _ info.CharacterProfile) error {
	c := char{}
	c.Character = tmpl.NewWithWrapper(s, w)

	c.EnergyMax = 60
	c.NormalHitNum = normalHitNum
	c.SkillCon = 3
	c.BurstCon = 5

	w.Character = &c

	return nil
}

func (c *char) Init() error {
	return nil
}
