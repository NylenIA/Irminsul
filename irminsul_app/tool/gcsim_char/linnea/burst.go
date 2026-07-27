package linnea

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Ultime (60 énergie, CD 15 s) : soin d'équipe calculé sur la DÉF — soin
// initial puis soin continu pendant 12 s. Valeurs exactes (tables du jeu).
// APPROXIMÉ : frames et cadence des ticks (un par seconde).
var burstFrames []int

const (
	burstHitmark = 38
	burstCD      = 15 * 60
	healTick     = 60
)

func init() {
	burstFrames = frames.InitAbilSlice(92)
	burstFrames[action.ActionAttack] = 84
	burstFrames[action.ActionAim] = 84
	burstFrames[action.ActionSkill] = 82
	burstFrames[action.ActionDash] = 80
	burstFrames[action.ActionJump] = 80
	burstFrames[action.ActionSwap] = 83
}

func (c *char) Burst(p map[string]int) (action.Info, error) {
	def := c.TotalDef(false)

	// soin initial : param2 % DÉF + param1 (plat)
	c.QueueCharTask(func() {
		c.Core.Player.Heal(info.HealInfo{
			Caller:  c.Index(),
			Target:  -1,
			Message: "Survival Guide (initial)",
			Src: burstP2[c.TalentLvlBurst()]*def +
				burstP1[c.TalentLvlBurst()],
			Bonus: c.Stat(attributes.Heal),
		})
	}, burstHitmark)

	// soin continu : param4 % DÉF + param3, pendant param5 secondes
	dur := int(burstP5[c.TalentLvlBurst()] * 60)
	for t := burstHitmark + healTick; t < burstHitmark+dur; t += healTick {
		c.QueueCharTask(func() {
			c.Core.Player.Heal(info.HealInfo{
				Caller:  c.Index(),
				Target:  -1,
				Message: "Survival Guide (continu)",
				Src: burstP4[c.TalentLvlBurst()]*def +
					burstP3[c.TalentLvlBurst()],
				Bonus: c.Stat(attributes.Heal),
			})
		}, t)
	}

	c.SetCDWithDelay(action.ActionBurst, burstCD, 10)
	c.ConsumeEnergy(8)

	return action.Info{
		Frames:          frames.NewAbilFunc(burstFrames),
		AnimationLength: burstFrames[action.InvalidAction],
		CanQueueAfter:   burstHitmark,
		State:           action.BurstState,
	}, nil
}
