package zibai

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Compétence : bascule en « Lunar Phase Shift » (durée et CD exacts, tables du
// jeu) et, si des ennemis sont proches, déclenche Spirit Steed's Stride
// (2 instances Geo sur la DÉF).
// APPROXIMÉ : frames, 3 particules, et le cumul de Phase Shift Radiance qui
// conditionne normalement le déclenchement — ici la chevauchée part à chaque
// activation. Zibai est donc légèrement SUR-estimée sur ce point précis, et
// sous-estimée ailleurs (passifs absents) : à recaler par un test en jeu.
var (
	skillFrames   []int
	skillHitmarks = []int{22, 34}
)

const (
	particleICDKey  = "zibai-particle-icd"
	skillCDFrames   = 18 * 60 // param5 = 18 s
	phaseShiftFrame = 15 * 60 // param4 = 15 s
)

func init() {
	skillFrames = frames.InitAbilSlice(52)
	skillFrames[action.ActionAttack] = 41
	skillFrames[action.ActionCharge] = 41
	skillFrames[action.ActionBurst] = 39
	skillFrames[action.ActionDash] = 33
	skillFrames[action.ActionJump] = 33
	skillFrames[action.ActionSwap] = 37
}

func (c *char) Skill(p map[string]int) (action.Info, error) {
	// entrée en mode lunaire
	c.AddStatus(phaseShiftKey, phaseShiftFrame, true)

	// Spirit Steed's Stride : 2 instances Geo sur la DÉF
	mults := []float64{
		skillP1[c.TalentLvlSkill()],
		skillP2[c.TalentLvlSkill()],
	}
	// A1 : le 2ᵉ coup de la chevauchée gagne 60 % de la DÉF pendant 4 s
	c.AddStatus(a1Key, 4*60, true)

	for i, m := range mults {
		ai := info.AttackInfo{
			ActorIndex: c.Index(),
			Abil:       "Spirit Steed's Stride",
			AttackTag:  attacks.AttackTagElementalArt,
			ICDTag:     attacks.ICDTagElementalArt,
			ICDGroup:   attacks.ICDGroupDefault,
			StrikeType: attacks.StrikeTypeDefault,
			Element:    attributes.Geo,
			Durability: 25,
			UseDef:     true,
			Mult:       m,
		}
		if i == 1 {
			// A1, renforcé par C2 si l'équipe est en Ascendant Gleam
			ai.FlatDmg = c.a1Bonus() + c.c2A1Bonus()
		}
		c.QueueCharTask(func() {
			c.Core.QueueAttack(
				ai,
				combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
					nil, 2.5),
				0, 0)
		}, skillHitmarks[i])
	}

	c.QueueCharTask(c.particleCB, skillHitmarks[0])
	c.SetCDWithDelay(action.ActionSkill, skillCDFrames, 14)

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
	c.Core.QueueParticle(c.Base.Key.String(), 3, attributes.Geo,
		c.ParticleDelay)
}
