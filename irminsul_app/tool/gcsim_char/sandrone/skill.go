package sandrone

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Compétence : elle embarque sur l'hovermech et, s'il y a des ennemis à
// proximité, tire 2 « Prism Shots » en DGT Cryo.
// EXACT : multiplicateurs, CD (4 s, table du jeu).
// APPROXIMÉ : frames, et 3 particules (valeur usuelle d'un 5★) — à confirmer.
var (
	skillFrames   []int
	skillHitmarks = []int{18, 30}
)

const (
	particleICDKey = "sandrone-particle-icd"
	skillCD        = 4 * 60
)

func init() {
	skillFrames = frames.InitAbilSlice(48)
	skillFrames[action.ActionAttack] = 38
	skillFrames[action.ActionCharge] = 38
	skillFrames[action.ActionBurst] = 36
	skillFrames[action.ActionDash] = 30
	skillFrames[action.ActionJump] = 30
	skillFrames[action.ActionSwap] = 34
}

func (c *char) Skill(p map[string]int) (action.Info, error) {
	mults := []float64{
		skillP1[c.TalentLvlSkill()],
		skillP2[c.TalentLvlSkill()],
	}
	for i, m := range mults {
		ai := info.AttackInfo{
			ActorIndex: c.Index(),
			Abil:       "Prism Shot",
			AttackTag:  attacks.AttackTagElementalArt,
			ICDTag:     attacks.ICDTagElementalArt,
			ICDGroup:   attacks.ICDGroupDefault,
			StrikeType: attacks.StrikeTypeDefault,
			Element:    attributes.Cryo,
			Durability: 25,
			Mult:       m,
		}
		c.QueueCharTask(func() {
			c.Core.QueueAttack(
				ai,
				combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
					nil, 2.0),
				0, 0)
		}, skillHitmarks[i])
	}

	c.QueueCharTask(c.particleCB, skillHitmarks[0])
	c.SetCDWithDelay(action.ActionSkill, skillCD, 12)

	return action.Info{
		Frames:          frames.NewAbilFunc(skillFrames),
		AnimationLength: skillFrames[action.InvalidAction],
		CanQueueAfter:   skillHitmarks[0],
		State:           action.SkillState,
	}, nil
}

func (c *char) particleCB() {
	if c.StatusIsActive(particleICDKey) {
		return
	}
	c.AddStatus(particleICDKey, 0.3*60, true)
	c.Core.QueueParticle(c.Base.Key.String(), 3, attributes.Cryo,
		c.ParticleDelay)
}
