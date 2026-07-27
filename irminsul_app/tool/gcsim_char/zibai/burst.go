package zibai

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Ultime : deux instances Geo sur la DÉF, la SECONDE comptée comme
// Lunar-Crystallize (réaction que le moteur connaît). Si Zibai est en Phase
// Shift, la durée du mode est prolongée de 1,7 s (description officielle).
// EXACT : multiplicateurs, CD 15 s, 60 énergie. APPROXIMÉ : frames.
var (
	burstFrames   []int
	burstHitmarks = []int{40, 56}
)

const (
	burstCD           = 15 * 60
	phaseShiftExtend  = 102 // 1,7 s
)

func init() {
	burstFrames = frames.InitAbilSlice(96)
	burstFrames[action.ActionAttack] = 88
	burstFrames[action.ActionCharge] = 88
	burstFrames[action.ActionSkill] = 86
	burstFrames[action.ActionDash] = 84
	burstFrames[action.ActionJump] = 84
	burstFrames[action.ActionSwap] = 87
}

func (c *char) Burst(p map[string]int) (action.Info, error) {
	first := info.AttackInfo{
		ActorIndex: c.Index(),
		Abil:       "Tri-Sphere Eminence",
		AttackTag:  attacks.AttackTagElementalBurst,
		ICDTag:     attacks.ICDTagElementalBurst,
		ICDGroup:   attacks.ICDGroupDefault,
		StrikeType: attacks.StrikeTypeDefault,
		Element:    attributes.Geo,
		Durability: 25,
		UseDef:     true,
		Mult:       burstP1[c.TalentLvlBurst()],
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			first,
			combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
				nil, 4.0),
			0, 0)
	}, burstHitmarks[0])

	second := first
	second.Abil = "Tri-Sphere Eminence (Lunar-Crystallize)"
	second.AttackTag = attacks.AttackTagDirectLunarCrystallize
	second.ICDTag = attacks.ICDTagNone
	second.Durability = 0
	second.Mult = burstP2[c.TalentLvlBurst()]
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			second,
			combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
				nil, 4.0),
			0, 0)
	}, burstHitmarks[1])

	// prolongation du mode lunaire si déjà actif
	if c.inPhaseShift() {
		c.AddStatus(phaseShiftKey,
			c.StatusDuration(phaseShiftKey)+phaseShiftExtend, true)
	}

	c.SetCDWithDelay(action.ActionBurst, burstCD, 10)
	c.ConsumeEnergy(8)

	return action.Info{
		Frames:          frames.NewAbilFunc(burstFrames),
		AnimationLength: burstFrames[action.InvalidAction],
		CanQueueAfter:   burstHitmarks[0],
		State:           action.BurstState,
	}, nil
}
