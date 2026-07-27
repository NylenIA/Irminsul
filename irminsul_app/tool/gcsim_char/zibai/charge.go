package zibai

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Attaque chargée en deux instances (P6+P7 hors mode, P11+P12 en Phase Shift,
// ces dernières sur la DÉF et en Geo). Frames APPROXIMÉES.
var (
	chargeFrames   []int
	chargeHitmarks = []int{20, 28}
)

func init() {
	chargeFrames = frames.InitAbilSlice(52)
	chargeFrames[action.ActionAttack] = 44
	chargeFrames[action.ActionSkill] = 42
	chargeFrames[action.ActionBurst] = 42
	chargeFrames[action.ActionDash] = 38
	chargeFrames[action.ActionJump] = 38
	chargeFrames[action.ActionSwap] = 41
}

func (c *char) ChargeAttack(p map[string]int) (action.Info, error) {
	shift := c.inPhaseShift()
	mults := []float64{
		normalP6[c.TalentLvlAttack()],
		normalP7[c.TalentLvlAttack()],
	}
	if shift {
		mults = []float64{
			skillP11[c.TalentLvlSkill()],
			skillP12[c.TalentLvlSkill()],
		}
	}

	for i, m := range mults {
		ai := info.AttackInfo{
			ActorIndex:   c.Index(),
			Abil:         "Charged Attack",
			AttackTag:    attacks.AttackTagExtra,
			ICDTag:       attacks.ICDTagNormalAttack,
			ICDGroup:     attacks.ICDGroupDefault,
			StrikeType:   attacks.StrikeTypeSlash,
			Element:      attributes.Physical,
			Durability:   25,
			Mult:         m,
			HitlagFactor: 0.01,
		}
		if shift {
			ai.Abil = "Phase Shift Charged Attack"
			ai.Element = attributes.Geo
			ai.UseDef = true
		}
		c.QueueCharTask(func() {
			c.Core.QueueAttack(
				ai,
				combat.NewCircleHitOnTarget(c.Core.Combat.Player(),
					info.Point{Y: 0.5}, 2.0),
				0, 0)
		}, chargeHitmarks[i])
	}

	return action.Info{
		Frames:          frames.NewAbilFunc(chargeFrames),
		AnimationLength: chargeFrames[action.InvalidAction],
		CanQueueAfter:   chargeHitmarks[1],
		State:           action.ChargeAttackState,
	}, nil
}
