package sandrone

import (
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/player/character"
	"github.com/genshinsim/gcsim/pkg/modifier"
)

// Passifs de Sandrone.
//
// A4 « A Lady's Code of Conduct » : +8 de maîtrise élémentaire par tranche de
// 100 ATQ, plafonné à +160. Implémenté — valeurs certaines.
//
// CE QUI NE PEUT PAS ENCORE L'ÊTRE, et pourquoi :
//
// Innée « Light of Rationalisme » : quand l'équipe déclenche un
// SUPRACONDUCTEUR, il devient un STELLAR-CONDUCT, et les DGT de base de
// Stellar-Conduct montent de 0,7 % par 100 ATQ de Sandrone (max 14 %). C'est
// exactement le pendant du passif de Zibai pour Lunar-Crystallize… sauf que
// le moteur ne connaît pas Stellar-Conduct : il gère Lunar-Charged,
// Lunar-Bloom et Lunar-Crystallize, pas celle-ci. Il n'existe donc ni tag
// d'attaque ni drapeau à activer.
// Les seules valeurs qui circulent viennent d'articles de leak : je ne les
// code pas. Tant que la réaction n'est pas ajoutée au cœur du moteur avec des
// chiffres vérifiables (ligne A5 du backlog), Sandrone reste SOUS-estimée —
// et c'est d'autant plus visible que le cycle d'Abîme en cours amplifie
// justement Supraconducteur et Stellar-Conduct.
//
// A1 « Eternal Speculation Engine » : dépend du cumul « Decoding Power » de
// Fagio, qui n'est pas modélisé. Non implémenté.

const (
	a4EmPer100Atk = 8.0
	a4EmCap       = 160.0
)

func (c *char) a4() {
	if c.Base.Ascension < 4 {
		return
	}
	m := make([]float64, attributes.EndStatType)
	c.AddStatMod(character.StatMod{
		Base:         modifier.NewBase("sandrone-a4", -1),
		AffectedStat: attributes.EM,
		Amount: func() []float64 {
			em := c.TotalAtk() / 100 * a4EmPer100Atk
			if em > a4EmCap {
				em = a4EmCap
			}
			m[attributes.EM] = em
			return m
		},
	})
}
