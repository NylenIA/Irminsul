package linnea

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Compétence (CD 18 s) : invoque « Lumi », qui frappe hors terrain en DGT Geo
// calculés sur la DÉF, pendant 25 s.
// EXACT : multiplicateurs des trois attaques de Lumi, durée, CD.
// APPROXIMÉ : la cadence réelle des coups. On répartit ici un cycle
// (2 × Pound-Pound + Heavy Overdrive + Million Ton Crush) toutes les 6 s,
// ce qui donne un rythme plausible mais à recaler par un test en jeu.
var skillFrames []int

const (
	skillHitmark   = 20
	particleICDKey = "linnea-particle-icd"
	skillCD        = 18 * 60
	lumiCycle      = 6 * 60
)

func init() {
	skillFrames = frames.InitAbilSlice(46)
	skillFrames[action.ActionAttack] = 37
	skillFrames[action.ActionAim] = 37
	skillFrames[action.ActionBurst] = 35
	skillFrames[action.ActionDash] = 30
	skillFrames[action.ActionJump] = 30
	skillFrames[action.ActionSwap] = 34
}

func (c *char) Skill(p map[string]int) (action.Info, error) {
	base := info.AttackInfo{
		ActorIndex: c.Index(),
		AttackTag:  attacks.AttackTagElementalArt,
		ICDTag:     attacks.ICDTagElementalArt,
		ICDGroup:   attacks.ICDGroupDefault,
		StrikeType: attacks.StrikeTypeDefault,
		Element:    attributes.Geo,
		Durability: 25,
		UseDef:     true,
	}

	// durée de Lumi : param4 de la compétence (25 s au niveau 10)
	dur := int(skillP4[c.TalentLvlSkill()] * 60)
	for t := skillHitmark; t < dur; t += lumiCycle {
		// Pound-Pound Pummeler : deux coups
		for k := 0; k < 2; k++ {
			ai := base
			ai.Abil = "Lumi: Pound-Pound Pummeler"
			ai.Mult = skillP1[c.TalentLvlSkill()]
			delay := t + k*18
			c.QueueCharTask(func() {
				c.Core.QueueAttack(ai,
					combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
						nil, 2.5), 0, 0)
			}, delay)
		}
		// Heavy Overdrive Hammer
		ai2 := base
		ai2.Abil = "Lumi: Heavy Overdrive Hammer"
		ai2.Mult = skillP2[c.TalentLvlSkill()]
		d2 := t + 60
		c.QueueCharTask(func() {
			c.Core.QueueAttack(ai2,
				combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
					nil, 2.5), 0, 0)
		}, d2)
		// Million Ton Crush
		ai3 := base
		ai3.Abil = "Lumi: Million Ton Crush"
		ai3.Mult = skillP3[c.TalentLvlSkill()]
		d3 := t + 150
		c.QueueCharTask(func() {
			c.Core.QueueAttack(ai3,
				combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
					nil, 3.0), 0, 0)
		}, d3)
	}

	c.QueueCharTask(c.particleCB, skillHitmark)
	c.SetCDWithDelay(action.ActionSkill, skillCD, 12)

	return action.Info{
		Frames:          frames.NewAbilFunc(skillFrames),
		AnimationLength: skillFrames[action.InvalidAction],
		CanQueueAfter:   skillHitmark,
		State:           action.SkillState,
	}, nil
}

func (c *char) particleCB() {
	if c.StatusIsActive(particleICDKey) {
		return
	}
	c.AddStatus(particleICDKey, 0.3*60, true)
	c.Core.QueueParticle(c.Base.Key.String(), 3, attributes.Geo,
		c.ParticleDelay)
}
