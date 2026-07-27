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

// Chaîne de 3 coups (description officielle : « up to 3 consecutive strikes »).
// Multiplicateurs exacts ; frames APPROXIMÉES sur un claymore standard.
var (
	attackFrames   [][]int
	attackHitmarks = []int{24, 26, 40}
	attackHitboxes = []float64{2.2, 2.2, 2.6}
	attackOffsets  = []float64{0.6, 0.6, 0.8}
)

const normalHitNum = 3

func init() {
	attackFrames = make([][]int, normalHitNum)

	attackFrames[0] = frames.InitNormalCancelSlice(attackHitmarks[0], 43)
	attackFrames[0][action.ActionAttack] = 33
	attackFrames[0][action.ActionCharge] = 30

	attackFrames[1] = frames.InitNormalCancelSlice(attackHitmarks[1], 46)
	attackFrames[1][action.ActionAttack] = 36
	attackFrames[1][action.ActionCharge] = 32

	attackFrames[2] = frames.InitNormalCancelSlice(attackHitmarks[2], 76)
	attackFrames[2][action.ActionAttack] = 70
	attackFrames[2][action.ActionCharge] = 62
}

func (c *char) Attack(p map[string]int) (action.Info, error) {
	mult := [][]float64{normalP1, normalP2, normalP3}[c.NormalCounter]

	ai := info.AttackInfo{
		ActorIndex:         c.Index(),
		Abil:               fmt.Sprintf("Normal %v", c.NormalCounter),
		AttackTag:          attacks.AttackTagNormal,
		ICDTag:             attacks.ICDTagNormalAttack,
		ICDGroup:           attacks.ICDGroupDefault,
		StrikeType:         attacks.StrikeTypeBlunt,
		Element:            attributes.Physical,
		Durability:         25,
		Mult:               mult[c.TalentLvlAttack()],
		HitlagFactor:       0.01,
		CanBeDefenseHalted: true,
	}
	ap := combat.NewCircleHitOnTarget(
		c.Core.Combat.Player(),
		info.Point{Y: attackOffsets[c.NormalCounter]},
		attackHitboxes[c.NormalCounter],
	)
	c.QueueCharTask(func() {
		c.Core.QueueAttack(ai, ap, 0, 0)
	}, attackHitmarks[c.NormalCounter])

	defer c.AdvanceNormalIndex()

	return action.Info{
		Frames:          frames.NewAttackFunc(c.Character, attackFrames),
		AnimationLength: attackFrames[c.NormalCounter][action.InvalidAction],
		CanQueueAfter:   attackHitmarks[c.NormalCounter],
		State:           action.NormalAttackState,
	}, nil
}
