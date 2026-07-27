// A Teaspoon of Transcendence — arme signature de Sandrone (6.7).
//
// EXACT (tables du jeu, voir le fichier généré) : ATQ de base, courbe de
// croissance, statistique secondaire (DGT CRIT) et paliers d'ascension. C'est
// ce qui pesait dans les calculs et qui manquait totalement : sans cette
// arme, toute simulation avec Sandrone échouait (« invalid weapon »).
//
// NON MODÉLISÉ : le passif de l'arme. Les statistiques s'appliquent, pas son
// effet. Sandrone est donc sous-estimée tant que le passif n'est pas écrit.
package ateaspoonoftranscendence

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
	w := &Weapon{}
	// Les statistiques de base et la stat secondaire sont appliquées par le
	// moteur depuis le catalogue ; seul le passif reste à écrire.
	return w, nil
}
