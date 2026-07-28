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
	// Activation : `sandrone charge[radiance=1];` (crochets).
	//
	// MESURÉ le 2026-07-27 sur une box réelle : avec radiance=1 la sim rend
	// MOINS (2 345 dps contre 2 469). C'est normal et c'est le signe de la
	// limite ci-dessus : les multiplicateurs Stellar-Conduct sont plus bas
	// que les normaux (faisceau 161,5 % contre 242,3 %) parce qu'en jeu ils
	// sont compensés par les bonus de réaction lunaire — que le moteur ne
	// connaît pas. Donc : NE PAS utiliser ce mode pour comparer des équipes
	// tant que Stellar-Conduct n'est pas implémenté dans le cœur du moteur.
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
	c.a4()
	c.c2()
	return nil
}
