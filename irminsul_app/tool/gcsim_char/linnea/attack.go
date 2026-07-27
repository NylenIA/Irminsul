package linnea

import (
	"fmt"

	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Arc : 3 tirs en chaîne + tir visé. Frames APPROXIMÉES sur un arc standard.
var (
	attackFrames   [][]int
	attackHitmarks = []int{14, 17, 24}
)

const normalHitNum = 3

func init() {
	attackFrames = make([][]int, normalHitNum)
	ends := []int{26, 31, 52}
	nexts := []int{19, 24, 44}
	for i := 0; i < normalHitNum; i++ {
		attackFrames[i] = frames.InitNormalCancelSlice(attackHitmarks[i], ends[i])
		attackFrames[i][action.ActionAttack] = nexts[i]
		attackFrames[i][action.ActionAim] = nexts[i]
	}
}

func (c *char) Attack(p map[string]int) (action.Info, error) {
	i := c.NormalCounter
	ai := info.AttackInfo{
		ActorIndex:         c.Index(),
		Abil:               fmt.Sprintf("Normal %v", i),
		AttackTag:          attacks.AttackTagNormal,
		ICDTag:             attacks.ICDTagNormalAttack,
		ICDGroup:           attacks.ICDGroupDefault,
		StrikeType:         attacks.StrikeTypePierce,
		Element:            attributes.Physical,
		Durability:         25,
		Mult:               [][]float64{normalP1, normalP2, normalP3}[i][c.TalentLvlAttack()],
		HitlagFactor:       0.01,
		CanBeDefenseHalted: true,
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			ai,
			combat.NewBoxHitOnTarget(c.Core.Combat.Player(),
				nil, 0.1, 0.1),
			0, 0)
	}, attackHitmarks[i])

	defer c.AdvanceNormalIndex()

	return action.Info{
		Frames:          frames.NewAttackFunc(c.Character, attackFrames),
		AnimationLength: attackFrames[i][action.InvalidAction],
		CanQueueAfter:   attackHitmarks[i],
		State:           action.NormalAttackState,
	}, nil
}

var aimedFrames []int

const aimedHitmark = 68

func init() {
	aimedFrames = frames.InitAbilSlice(97)
	aimedFrames[action.ActionDash] = 0
	aimedFrames[action.ActionJump] = 0
}

func (c *char) Aimed(p map[string]int) (action.Info, error) {
	// tir visé pleinement chargé (multiplicateur du jeu)
	ai := info.AttackInfo{
		ActorIndex: c.Index(),
		Abil:       "Fully-Charged Aimed Shot",
		AttackTag:  attacks.AttackTagExtra,
		ICDTag:     attacks.ICDTagNone,
		ICDGroup:   attacks.ICDGroupDefault,
		StrikeType: attacks.StrikeTypePierce,
		Element:    attributes.Geo,
		Durability: 25,
		Mult:       normalP5[c.TalentLvlAttack()],
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			ai,
			combat.NewBoxHitOnTarget(c.Core.Combat.PrimaryTarget(),
				nil, 0.1, 0.1),
			0, 0)
	}, aimedHitmark)

	return action.Info{
		Frames:          frames.NewAbilFunc(aimedFrames),
		AnimationLength: aimedFrames[action.InvalidAction],
		CanQueueAfter:   aimedHitmark,
		State:           action.AimState,
	}, nil
}
