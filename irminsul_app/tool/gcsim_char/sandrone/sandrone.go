// Sandrone (6.7) — implémentation Irminsul, en attendant celle de la
// communauté gcsim.
//
// EXACT (tables du jeu, voir zz_sandrone_gen.go) : multiplicateurs par niveau
// de talent, stats de base, courbes, ascensions, coût d'ultime, CD.
//
// APPROXIMÉ et à confirmer par un test en jeu :
//   - frames d'animation (calées sur un porteur claymore comparable) ;
//   - particules d'énergie générées par la compétence (3, valeur usuelle 5★) ;
//   - le système « Decoding Power » de Fagio et la conversion Radiance :
//     Stellar-Conduct ne sont PAS modélisés — les faisceaux comptent en Cryo
//     normal. Les DGT réels d'une équipe Stellar-Conduct sont donc
//     sous-estimés, jamais sur-estimés.
//   - passifs et constellations : non implémentés.
package sandrone

import (
	tmpl "github.com/genshinsim/gcsim/internal/template/character"
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
)

type char struct {
	*tmpl.Character

	// État « Radiance : Stellar-Conduct ». Le moteur ne connaît PAS la
	// réaction Stellar-Conduct (il gère Lunar-Charged / Lunar-Bloom /
	// Lunar-Crystallize, pas celle-ci). On modélise donc ce qui est exact :
	// dans cet état, ses faisceaux, son 2ᵉ tir prismatique et son rayon
	// d'ultime utilisent LEURS PROPRES multiplicateurs (présents dans les
	// tables du jeu), infligés en Cryo.
	// Limite assumée : les effets qui réagissent au TYPE de réaction
	// (artefacts lunaires, bonus de cycle) ne se déclenchent pas.
	// Activation : paramètre `radiance=1` sur l'action.
	radiance bool
}

// radianceOn lit le paramètre d'action et mémorise l'état.
func (c *char) radianceOn(p map[string]int) bool {
	if v, ok := p["radiance"]; ok {
		c.radiance = v != 0
	}
	return c.radiance
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
