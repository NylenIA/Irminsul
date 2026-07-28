package illuga

import (
	"github.com/genshinsim/gcsim/pkg/core/attributes"
)

// Passifs d'Illuga.
//
// Innée « Moonsign Benediction : Unwithering in Winter » : sa présence fait
// monter le Moonsign de l'équipe d'un niveau. Avec Zibai ou Columbina,
// l'équipe atteint donc « Ascendant Gleam » (niveau 2, le maximum), ce qui
// amplifie toutes les réactions lunaires. C'est loin d'être un détail.
//
// A4 « Demonhunter's Dusk » : selon le nombre d'alliés Hydro ou Geo (1/2/3),
// le buff de son ultime augmente en plus de 7 % / 14 % / 24 % de SA maîtrise
// élémentaire. Interprétation retenue : ce supplément s'ajoute au bonus de
// dégâts plats déjà accordé par l'ultime (même forme, « X % de la MÉ »), ce
// qui est la lecture la plus directe du libellé du jeu.
//
// A1 « Torchforger's Covenant » : après compétence ou ultime, les alliés
// gagnent « Lightkeeper's Oath » 20 s, un effet lié aux DGT Geo dont le
// libellé public est tronqué. NON implémenté — je ne complète pas au jugé.

const (
	a4Em1 = 0.07
	a4Em2 = 0.14
	a4Em3 = 0.24
)

func (c *char) innate() {
	c.Moonsign = 1
}

// a4Bonus : supplément de dégâts plats apporté par le A4, selon la
// composition de l'équipe. Retourne 0 si le palier d'ascension n'est pas
// atteint.
func (c *char) a4Bonus() float64 {
	if c.Base.Ascension < 4 {
		return 0
	}
	n := 0
	for _, x := range c.Core.Player.Chars() {
		if x.Index() == c.Index() {
			continue
		}
		switch x.Base.Element {
		case attributes.Geo, attributes.Hydro:
			n++
		}
	}
	var pct float64
	switch {
	case n >= 3:
		pct = a4Em3
	case n == 2:
		pct = a4Em2
	case n == 1:
		pct = a4Em1
	default:
		return 0
	}
	return pct * c.NonExtraStat(attributes.EM)
}
