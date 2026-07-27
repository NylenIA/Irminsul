package sandrone

import (
	"fmt"

	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Ultime : bombardement (×3) puis « Convective Inhibition Ray », DGT Cryo de
// zone. EXACT : multiplicateurs, CD 15 s, 60 énergie.
// APPROXIMÉ : frames et espacement des trois bombardements.
var (
	burstFrames    []int
	burstHitmarks  = []int{46, 58, 70}
	burstRayHitmar = 92
)

const burstCD = 15 * 60

func init() {
	burstFrames = frames.InitAbilSlice(112)
	burstFrames[action.ActionAttack] = 104
	burstFrames[action.ActionCharge] = 104
	burstFrames[action.ActionSkill] = 102
	burstFrames[action.ActionDash] = 100
	burstFrames[action.ActionJump] = 100
	burstFrames[action.ActionSwap] = 103
}

func (c *char) Burst(p map[string]int) (action.Info, error) {
	// 3 bombardements
	for i, hit := range burstHitmarks {
		ai := info.AttackInfo{
			ActorIndex: c.Index(),
			Abil:       fmt.Sprintf("Bombardment %v", i+1),
			AttackTag:  attacks.AttackTagElementalBurst,
			ICDTag:     attacks.ICDTagElementalBurst,
			ICDGroup:   attacks.ICDGroupDefault,
			StrikeType: attacks.StrikeTypeDefault,
			Element:    attributes.Cryo,
			Durability: 25,
			Mult:       burstP1[c.TalentLvlBurst()],
		}
		c.QueueCharTask(func() {
			c.Core.QueueAttack(
				ai,
				combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
					nil, 4.0),
				0, 0)
		}, hit)
	}

	// rayon final
	ray := info.AttackInfo{
		ActorIndex: c.Index(),
		Abil:       "Convective Inhibition Ray",
		AttackTag:  attacks.AttackTagElementalBurst,
		ICDTag:     attacks.ICDTagElementalBurst,
		ICDGroup:   attacks.ICDGroupDefault,
		StrikeType: attacks.StrikeTypeDefault,
		Element:    attributes.Cryo,
		Durability: 25,
		Mult:       burstP2[c.TalentLvlBurst()],
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			ray,
			combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
				nil, 5.0),
			0, 0)
	}, burstRayHitmar)

	c.SetCDWithDelay(action.ActionBurst, burstCD, 10)
	c.ConsumeEnergy(9)

	return action.Info{
		Frames:          frames.NewAbilFunc(burstFrames),
		AnimationLength: burstFrames[action.InvalidAction],
		CanQueueAfter:   burstHitmarks[0],
		State:           action.BurstState,
	}, nil
}
