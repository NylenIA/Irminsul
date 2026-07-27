package sandrone

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Attaque chargée : Fagio passe en mode « Decoding » — tir de balayage puis
// faisceau condensé, tous deux en DGT Cryo de zone.
// APPROXIMATION assumée : le cumul de « Decoding Power » et la conversion
// Radiance : Stellar-Conduct ne sont pas modélisés ; le faisceau compte en
// Cryo normal. Sous-estimation, jamais surestimation.
var (
	chargeFrames    []int
	chargeHitmarks  = []int{33, 47}
	chargeHitbox    = 3.0
	chargeStamina   = 20.0
	chargeFrameLast = 78
)

func init() {
	chargeFrames = frames.InitAbilSlice(chargeFrameLast)
	chargeFrames[action.ActionAttack] = 70
	chargeFrames[action.ActionSkill] = 66
	chargeFrames[action.ActionBurst] = 66
	chargeFrames[action.ActionDash] = 62
	chargeFrames[action.ActionJump] = 62
	chargeFrames[action.ActionSwap] = 68
}

func (c *char) ChargeAttack(p map[string]int) (action.Info, error) {
	// 1) tir de balayage
	sweep := info.AttackInfo{
		ActorIndex:   c.Index(),
		Abil:         "Charged Attack (Sweeping Fire)",
		AttackTag:    attacks.AttackTagExtra,
		ICDTag:       attacks.ICDTagNormalAttack,
		ICDGroup:     attacks.ICDGroupDefault,
		StrikeType:   attacks.StrikeTypeDefault,
		Element:      attributes.Cryo,
		Durability:   25,
		Mult:         normalP4[c.TalentLvlAttack()],
		HitlagFactor: 0.01,
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			sweep,
			combat.NewCircleHitOnTarget(c.Core.Combat.Player(),
				info.Point{Y: 0.8}, chargeHitbox),
			0, 0)
	}, chargeHitmarks[0])

	// 2) faisceau condensé — en Radiance, le multiplicateur Stellar-Conduct
	// (exact, table du jeu) remplace celui du faisceau normal.
	beam := sweep
	beam.Abil = "Charged Attack (Condensed Beam)"
	beam.Mult = normalP5[c.TalentLvlAttack()]
	if c.radianceOn(p) {
		beam.Abil = "Charged Attack (Condensed Beam, Stellar-Conduct)"
		beam.Mult = normalP6[c.TalentLvlAttack()]
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			beam,
			combat.NewCircleHitOnTarget(c.Core.Combat.Player(),
				info.Point{Y: 1.0}, chargeHitbox),
			0, 0)
	}, chargeHitmarks[1])

	return action.Info{
		Frames:          frames.NewAbilFunc(chargeFrames),
		AnimationLength: chargeFrames[action.InvalidAction],
		CanQueueAfter:   chargeHitmarks[1],
		State:           action.ChargeAttackState,
	}, nil
}
