// Illuga — pièce maîtresse de la meilleure équipe de Zibai selon KQM
// (Zibai — Illuga — Linnea — Columbina). Sans lui, impossible de simuler la
// BiS : il n'existait pas dans gcsim.
//
// EXACT (tables du jeu, voir le fichier généré) : multiplicateurs, scalings
// sur la Maîtrise élémentaire ET la DÉF, durée du buff, CD, coût d'ultime.
//
// Ce qui fait tout son intérêt et qui EST modélisé : son ultime accorde à
// l'équipe un bonus de dégâts PLATS, calculé sur SA maîtrise élémentaire —
// un bonus sur les DGT Geo, et un bonus bien plus gros sur les dégâts de
// réaction Lunar-Crystallize (celle que déclenche Zibai).
//
// APPROXIMÉ, à confirmer en jeu : frames, particules (3), variante « hold »
// de la compétence non distinguée, cumuls « Nightingale's Song », passifs et
// constellations non implémentés.
package illuga

import (
	tmpl "github.com/genshinsim/gcsim/internal/template/character"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
)

const burstBuffKey = "illuga-nightingale-song"

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
	c.innate()
	c.burstBuffHook()
	return nil
}
