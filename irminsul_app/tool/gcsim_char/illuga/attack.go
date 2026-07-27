package illuga

import (
	"fmt"

	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Chaîne de 4 coups à la lance. Frames APPROXIMÉES sur une lance standard.
var (
	attackFrames   [][]int
	attackHitmarks = []int{16, 15, 22, 30}
	attackHitboxes = []float64{1.8, 1.8, 2.0, 2.2}
	attackOffsets  = []float64{0.5, 0.5, 0.6, 0.7}
)

const normalHitNum = 4

func init() {
	attackFrames = make([][]int, normalHitNum)
	ends := []int{30, 32, 44, 66}
	nexts := []int{21, 23, 35, 58}
	for i := 0; i < normalHitNum; i++ {
		attackFrames[i] = frames.InitNormalCancelSlice(attackHitmarks[i], ends[i])
		attackFrames[i][action.ActionAttack] = nexts[i]
		attackFrames[i][action.ActionCharge] = nexts[i]
	}
}

func (c *char) Attack(p map[string]int) (action.Info, error) {
	i := c.NormalCounter
	mult := [][]float64{normalP1, normalP2, normalP3, normalP5}[i][c.TalentLvlAttack()]

	ai := info.AttackInfo{
		ActorIndex:         c.Index(),
		Abil:               fmt.Sprintf("Normal %v", i),
		AttackTag:          attacks.AttackTagNormal,
		ICDTag:             attacks.ICDTagNormalAttack,
		ICDGroup:           attacks.ICDGroupDefault,
		StrikeType:         attacks.StrikeTypePierce,
		Element:            attributes.Physical,
		Durability:         25,
		Mult:               mult,
		HitlagFactor:       0.01,
		CanBeDefenseHalted: true,
	}
	ap := combat.NewCircleHitOnTarget(
		c.Core.Combat.Player(),
		info.Point{Y: attackOffsets[i]},
		attackHitboxes[i],
	)
	c.QueueCharTask(func() {
		c.Core.QueueAttack(ai, ap, 0, 0)
	}, attackHitmarks[i])

	// le 3ᵉ coup porte deux instances (libellés du jeu : param3 + param4)
	if i == 2 {
		extra := ai
		extra.Abil += " (2)"
		extra.Mult = normalP4[c.TalentLvlAttack()]
		c.QueueCharTask(func() {
			c.Core.QueueAttack(extra, ap, 0, 0)
		}, attackHitmarks[i]+5)
	}

	defer c.AdvanceNormalIndex()

	return action.Info{
		Frames:          frames.NewAttackFunc(c.Character, attackFrames),
		AnimationLength: attackFrames[i][action.InvalidAction],
		CanQueueAfter:   attackHitmarks[i],
		State:           action.NormalAttackState,
	}, nil
}

var chargeFrames []int

const chargeHitmark = 26

func init() {
	chargeFrames = frames.InitAbilSlice(48)
	chargeFrames[action.ActionAttack] = 42
	chargeFrames[action.ActionSkill] = 40
	chargeFrames[action.ActionBurst] = 40
	chargeFrames[action.ActionDash] = 36
	chargeFrames[action.ActionJump] = 36
	chargeFrames[action.ActionSwap] = 39
}

func (c *char) ChargeAttack(p map[string]int) (action.Info, error) {
	ai := info.AttackInfo{
		ActorIndex:   c.Index(),
		Abil:         "Charged Attack",
		AttackTag:    attacks.AttackTagExtra,
		ICDTag:       attacks.ICDTagNormalAttack,
		ICDGroup:     attacks.ICDGroupDefault,
		StrikeType:   attacks.StrikeTypePierce,
		Element:      attributes.Physical,
		Durability:   25,
		Mult:         normalP6[c.TalentLvlAttack()],
		HitlagFactor: 0.01,
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			ai,
			combat.NewCircleHitOnTarget(c.Core.Combat.Player(),
				info.Point{Y: 0.6}, 2.2),
			0, 0)
	}, chargeHitmark)

	return action.Info{
		Frames:          frames.NewAbilFunc(chargeFrames),
		AnimationLength: chargeFrames[action.InvalidAction],
		CanQueueAfter:   chargeHitmark,
		State:           action.ChargeAttackState,
	}, nil
}
