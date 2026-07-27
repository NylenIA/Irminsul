package illuga

import (
	"github.com/genshinsim/gcsim/internal/frames"
	"github.com/genshinsim/gcsim/pkg/core/action"
	"github.com/genshinsim/gcsim/pkg/core/attacks"
	"github.com/genshinsim/gcsim/pkg/core/attributes"
	"github.com/genshinsim/gcsim/pkg/core/combat"
	"github.com/genshinsim/gcsim/pkg/core/event"
	"github.com/genshinsim/gcsim/pkg/core/glog"
	"github.com/genshinsim/gcsim/pkg/core/info"
)

// Ultime (60 énergie, CD 15 s) : dégâts Geo (MÉ + DÉF) puis, pendant 21 s,
// un BONUS DE DÉGÂTS PLATS pour toute l'équipe, calculé sur la maîtrise
// élémentaire d'Illuga :
//   - sur les DGT Geo ;
//   - bien plus gros sur les dégâts de réaction Lunar-Crystallize, celle que
//     Zibai déclenche. C'est la raison d'être de cette équipe.
// Toutes ces valeurs viennent des tables du jeu. APPROXIMÉ : frames, et les
// cumuls « Nightingale's Song » (obtenus via constructions Geo) ne sont pas
// modélisés — le buff est donc appliqué à son niveau de base.
var burstFrames []int

const (
	burstHitmark = 44
	burstCD      = 15 * 60
)

func init() {
	burstFrames = frames.InitAbilSlice(98)
	burstFrames[action.ActionAttack] = 90
	burstFrames[action.ActionCharge] = 90
	burstFrames[action.ActionSkill] = 88
	burstFrames[action.ActionDash] = 86
	burstFrames[action.ActionJump] = 86
	burstFrames[action.ActionSwap] = 89
}

func (c *char) Burst(p map[string]int) (action.Info, error) {
	ai := info.AttackInfo{
		ActorIndex: c.Index(),
		Abil:       "Shadowless Reflection",
		AttackTag:  attacks.AttackTagElementalBurst,
		ICDTag:     attacks.ICDTagElementalBurst,
		ICDGroup:   attacks.ICDGroupDefault,
		StrikeType: attacks.StrikeTypeDefault,
		Element:    attributes.Geo,
		Durability: 25,
		UseDef:     true,
		Mult:       burstP2[c.TalentLvlBurst()],
		FlatDmg:    burstP1[c.TalentLvlBurst()] * c.NonExtraStat(attributes.EM),
	}
	c.QueueCharTask(func() {
		c.Core.QueueAttack(
			ai,
			combat.NewCircleHitOnTarget(c.Core.Combat.PrimaryTarget(),
				nil, 5.0),
			0, 0)
	}, burstHitmark)

	// durée du buff : param7 de l'ultime (21 s au niveau 10)
	dur := int(burstP7[c.TalentLvlBurst()] * 60)
	c.AddStatus(burstBuffKey, dur, true)

	c.SetCDWithDelay(action.ActionBurst, burstCD, 10)
	c.ConsumeEnergy(8)

	return action.Info{
		Frames:          frames.NewAbilFunc(burstFrames),
		AnimationLength: burstFrames[action.InvalidAction],
		CanQueueAfter:   burstHitmark,
		State:           action.BurstState,
	}, nil
}

// burstBuffHook ajoute les dégâts plats avant application, comme le fait
// Yun Jin pour son bonus basé sur la DÉF.
func (c *char) burstBuffHook() {
	c.Core.Events.Subscribe(event.OnEnemyHit, func(args ...any) {
		ae := args[1].(*info.AttackEvent)
		if !c.StatusIsActive(burstBuffKey) {
			return
		}
		em := c.NonExtraStat(attributes.EM)
		var added float64
		switch {
		case ae.Info.AttackTag == attacks.AttackTagDirectLunarCrystallize:
			added = burstP4[c.TalentLvlBurst()] * em
		case ae.Info.Element == attributes.Geo:
			added = burstP3[c.TalentLvlBurst()] * em
		default:
			return
		}
		ae.Info.FlatDmg += added
		c.Core.Log.NewEvent("illuga burst flat dmg", glog.LogPreDamageMod,
			ae.Info.ActorIndex).
			Write("added", added).
			Write("em", em)
	}, "illuga-burst-buff")
}
