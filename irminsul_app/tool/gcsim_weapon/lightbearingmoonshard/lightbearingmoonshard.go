// Lightbearing Moonshard — arme absente de gcsim, ajoutée par Irminsul.
//
// EXACT (tables du jeu, fichier généré à côté) : ATQ de base, courbe de
// croissance, statistique secondaire et paliers d'ascension. C'est ce qui
// pesait dans les calculs et manquait : sans cette arme, la simulation du
// personnage qui la porte échouait (« invalid weapon »).
//
// NON MODÉLISÉ : le passif. Les statistiques s'appliquent, pas son effet —
// le porteur est donc SOUS-estimé tant que ce fichier n'est pas complété.
package lightbearingmoonshard

import (
	"github.com/genshinsim/gcsim/pkg/core"
	"github.com/genshinsim/gcsim/pkg/core/info"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
)

type Weapon struct {
	Index int
}

func (w *Weapon) SetIndex(idx int) { w.Index = idx }
func (w *Weapon) Init() error      { return nil }

func NewWeapon(c *core.Core, char *character.CharWrapper, p info.WeaponProfile) (info.Weapon, error) {
	return &Weapon{}, nil
}
