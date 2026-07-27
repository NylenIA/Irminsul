package zibai

import (
	"fmt"

	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Chaîne de 4 coups. Frames APPROXIMÉES sur une épée standard.
// Hors Phase Shift : Physique, scaling ATQ.
// En Phase Shift : Geo non remplaçable, scaling DÉF, multiplicateurs propres,
// et le 4ᵉ coup ajoute une instance Lunar-Crystallize.
var (
	attackFrames   [][]int
	attackHitmarks = []int{13, 12, 19, 28}
	attackHitboxes = []float64{1.6, 1.6, 1.8, 2.0}
	attackOffsets  = []float64{0.4, 0.4, 0.5, 0.6}
)

const normalHitNum = 4

func init() {
	attackFrames = make([][]int, normalHitNum)

	attackFrames[0] = frames.InitNormalCancelSlice(attackHitmarks[0], 27)
	attackFrames[0][action.ActionAttack] = 18
	attackFrames[0][action.ActionCharge] = 17

	attackFrames[1] = frames.InitNormalCancelSlice(attackHitmarks[1], 29)
	attackFrames[1][action.ActionAttack] = 20
	attackFrames[1][action.ActionCharge] = 19

	attackFrames[2] = frames.InitNormalCancelSlice(attackHitmarks[2], 41)
	attackFrames[2][action.ActionAttack] = 33
	attackFrames[2][action.ActionCharge] = 31

	attackFrames[3] = frames.InitNormalCancelSlice(attackHitmarks[3], 62)
	attackFrames[3][action.ActionAttack] = 55
	attackFrames[3][action.ActionCharge] = 52
}

func (c *char) Attack(p map[string]int) (action.Info, error) {
	i := c.NormalCounter
	shift := c.inPhaseShift()

	ai := info.AttackInfo{
		ActorIndex:         c.Index(),
		Abil:               fmt.Sprintf("Normal %v", i),
		AttackTag:          attacks.AttackTagNormal,
		ICDTag:             attacks.ICDTagNormalAttack,
		ICDGroup:           attacks.ICDGroupDefault,
		StrikeType:         attacks.StrikeTypeSlash,
		Element:            attributes.Physical,
		Durability:         25,
		HitlagFactor:       0.01,
		CanBeDefenseHalted: true,
	}

	if shift {
		// mode lunaire : Geo, sur la DÉF, multiplicateurs dédiés
		ai.Abil = fmt.Sprintf("Phase Shift Normal %v", i)
		ai.Element = attributes.Geo
		ai.UseDef = true
		ai.Mult = []([]float64){skillP6, skillP7, skillP8, skillP10}[i][c.TalentLvlSkill()]
	} else {
		ai.Mult = []([]float64){normalP1, normalP2, normalP3, normalP5}[i][c.TalentLvlAttack()]
	}

	ap := combat.NewCircleHitOnTarget(
		c.Core.Combat.Player(),
		info.Point{Y: attackOffsets[i]},
		attackHitboxes[i],
	)
	c.QueueCharTask(func() {
		c.Core.QueueAttack(ai, ap, 0, 0)
	}, attackHitmarks[i])

	// 3ᵉ coup : seconde instance (les libellés du jeu donnent P3+P4 hors mode,
	// P8+P9 en Phase Shift)
	if i == 2 {
		extra := ai
		extra.Abil += " (2)"
		if shift {
			extra.Mult = skillP9[c.TalentLvlSkill()]
		} else {
			extra.Mult = normalP4[c.TalentLvlAttack()]
		}
		c.QueueCharTask(func() {
			c.Core.QueueAttack(extra, ap, 0, 0)
		}, attackHitmarks[i]+4)
	}

	// 4ᵉ coup en Phase Shift : instance supplémentaire comptée comme
	// Lunar-Crystallize (Moonsign : Ascendant Gleam)
	if shift && i == 3 {
		lunar := info.AttackInfo{
			ActorIndex: c.Index(),
			Abil:       "Phase Shift 4-Hit (Lunar-Crystallize)",
			AttackTag:  attacks.AttackTagDirectLunarCrystallize,
			ICDTag:     attacks.ICDTagNone,
			ICDGroup:   attacks.ICDGroupDefault,
			StrikeType: attacks.StrikeTypeDefault,
			Element:    attributes.Geo,
			Durability: 0,
			UseDef:     true,
			Mult:       skillP3[c.TalentLvlSkill()],
		}
		c.QueueCharTask(func() {
			c.Core.QueueAttack(lunar, ap, 0, 0)
		}, attackHitmarks[i]+6)
	}

	defer c.AdvanceNormalIndex()

	return action.Info{
		Frames:          frames.NewAttackFunc(c.Character, attackFrames),
		AnimationLength: attackFrames[i][action.InvalidAction],
		CanQueueAfter:   attackHitmarks[i],
		State:           action.NormalAttackState,
	}, nil
}
