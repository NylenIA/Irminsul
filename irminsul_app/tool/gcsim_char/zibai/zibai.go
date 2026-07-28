// Zibai (6.x) — implémentation Irminsul, en attendant celle de la commu.
//
// EXACT (tables du jeu, voir zz_zibai_gen.go) : multiplicateurs des deux modes
// d'attaque, scaling sur la DÉF, durée et CD de la compétence, coût d'ultime,
// stats de base et ascensions.
//
// Ce qui est réellement modélisé, parce que le moteur sait le faire :
//   - le mode « Lunar Phase Shift » : ses attaques normales passent en Geo et
//     scalent sur la DÉF (UseDef), avec leurs propres multiplicateurs ;
//   - le 4ᵉ coup en Phase Shift ajoute une instance comptée comme
//     Lunar-Crystallize (le moteur connaît cette réaction) ;
//   - l'ultime inflige 2 instances, la seconde en Lunar-Crystallize.
//
// APPROXIMÉ, à confirmer en jeu : frames d'animation, particules (3), et le
// cumul de « Phase Shift Radiance » qui déclenche Spirit Steed's Stride —
// non modélisé, donc Zibai est SOUS-estimée. Passifs et constellations non
// implémentés.
package zibai

import (
	tmpl "github.com/genshinsim/gcsim/internal/template/character"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
)

const phaseShiftKey = "zibai-lunar-phase-shift"

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
	c.a4()
	return nil
}

// inPhaseShift : ses normales changent complètement de nature dans ce mode.
func (c *char) inPhaseShift() bool {
	return c.StatusIsActive(phaseShiftKey)
}
