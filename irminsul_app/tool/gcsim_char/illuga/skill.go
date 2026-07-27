package illuga

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Compétence (CD 15 s) : DGT Geo qui scalent À LA FOIS sur la maîtrise
// élémentaire et sur la DÉF — les deux parts viennent des tables du jeu.
// APPROXIMÉ : frames, 3 particules, et la variante « hold » (multiplicateurs
// plus élevés) n'est pas distinguée du press.
var skillFrames []int

const (
	skillHitmark   = 24
	particleICDKey = "illuga-particle-icd"
	skillCD        = 15 * 60
)

func init() {
	skillFrames = frames.InitAbilSlice(50)
	skillFrames[action.ActionAttack] = 40
	skillFrames[action.ActionCharge] = 40
	skillFrames[action.ActionBurst] = 38
	skillFrames[action.ActionDash] = 33
	skillFrames[action.ActionJump] = 33
	skillFrames[action.ActionSwap] = 36
}

func (c *char) Skill(p map[string]int) (action.Info, error) {
	ai := info.AttackInfo{
		ActorIndex: c.Index(),
		Abil:       "Dawnbearing Songbird",
		AttackTag:  attacks.AttackTagElementalArt,
		ICDTag:     attacks.ICDTagElementalArt,
		ICDGroup:   attacks.ICDGroupDefault,
		StrikeType: attacks.StrikeTypeDefault,
		Element:    attributes.Geo,
		Durability: 25,
		// part DÉF via le moteur, part MÉ ajoutée en dégâts plats
		UseDef:  true,
		Mult:    skillP2[c.TalentLvlSkill()],
		FlatDmg: skillP1[c.TalentLvlSkill()] * c.NonExtraStat(attributes.EM),
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			ai,
			combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
				nil, 3.0),
			0, 0)
	}, skillHitmark)

	c.QueueCharTask(c.particleCB, skillHitmark)
	c.SetCDWithDelay(action.ActionSkill, skillCD, 14)

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
