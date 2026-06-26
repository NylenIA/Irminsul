"""Optimiseur d'équipes orienté calcul de dégâts.

Objectif : *construire/classer* la meilleure équipe d'un porteur en sommant les
buffs des supports dans la formule de dégâts réutilisée (`calculate_direct_hit`),
puis en générant et notant les combinaisons valides.

⚠️ C'est un **modèle analytique transparent** (plafond de buffs empilés), **pas un
gcsim**. Il capture l'empilement de buffs/debuffs et la réaction, mais PAS la
vitesse de rotation, l'énergie fine, l'application d'aura instantanée ni l'uptime.
→ À utiliser pour générer des candidats ; valider le top via gcsim.

Leçon encodée ici (cf. test) : sur un porteur ATK-scaling comme Mavuika, quand le
**debuff de RES est déjà couvert** (ex. Citlali shred le Pyro), un support 100 %
offensif (Iansan : +ATK% / +ATK plat / +DMG%) dépasse un support de RES shred
redondant (Xilonen). D'où le team plafond **Mavuika · Citlali · Iansan · Bennett**.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any

from .config import load_yaml
from .damage import calculate_direct_hit
from .paths import account_subdir, project_root
from .reaction import AMPLIFYING_BASE, amplifying_multiplier

# Élément qui sert d'activateur pour chaque réaction amplifiante (côté carry Pyro).
_ENABLER_ELEMENT = {"forward-melt": "cryo", "reverse-melt": "cryo",
                    "forward-vaporize": "hydro", "reverse-vaporize": "hydro"}

_BUFF_KEYS = ("atk_pct", "atk_flat", "dmg_bonus", "crit_rate", "crit_dmg",
              "em", "res_shred", "def_shred")


# --------------------------------------------------------------------------- #
# Données
# --------------------------------------------------------------------------- #
@dataclass
class Carry:
    name: str
    element: str = "pyro"
    region: str = ""
    scaling: float = 4.0          # multiplicateur représentatif (constant entre teams)
    base_atk: float = 1000.0
    atk_pct: float = 0.0
    atk_flat: float = 0.0
    crit_rate: float = 0.05
    crit_dmg: float = 1.0
    dmg_bonus: float = 0.0
    em: float = 0.0
    reaction: str | None = None   # réaction préférée par défaut
    needs_natlan: int = 0
    on_field: bool = True


@dataclass
class Support:
    name: str
    element: str = ""
    region: str = ""
    buffs: dict[str, float] = field(default_factory=dict)
    fighting_spirit: bool = False
    enables: tuple[str, ...] = ()       # réactions qu'il peut activer (via son élément)
    applies_aura: bool = False          # applique une aura gênante hors réaction
    on_field: bool = False


# Seed intégré (source de vérité ; config/support_profiles.yaml peut surcharger).
_SEED_CARRIES: dict[str, dict[str, Any]] = {
    "Mavuika": {
        "element": "pyro", "region": "natlan", "scaling": 4.0, "base_atk": 1050,
        "atk_pct": 0.45, "crit_rate": 0.65, "crit_dmg": 1.90, "dmg_bonus": 0.62,
        "em": 120, "reaction": "forward-melt", "needs_natlan": 2, "on_field": True,
    },
}

_SEED_SUPPORTS: dict[str, dict[str, Any]] = {
    "Citlali": {"element": "cryo", "region": "natlan", "fighting_spirit": True,
                "enables": ["forward-melt", "reverse-melt"],
                "buffs": {"res_shred": 0.20, "em": 125}},
    "Iansan": {"element": "electro", "region": "natlan", "fighting_spirit": True,
               "buffs": {"atk_pct": 0.30, "atk_flat": 700, "dmg_bonus": 0.25}},
    "Xilonen": {"element": "geo", "region": "natlan", "fighting_spirit": True,
                "buffs": {"res_shred": 0.36}},
    "Bennett": {"element": "pyro", "region": "mondstadt",
                "buffs": {"atk_flat": 1100}},
    "Furina": {"element": "hydro", "region": "fontaine", "applies_aura": True,
               "enables": ["forward-vaporize", "reverse-vaporize"],
               "buffs": {"dmg_bonus": 0.50}},
    "Kazuha": {"element": "anemo", "region": "inazuma",
               "buffs": {"res_shred": 0.40, "em": 200}},
    "Sucrose": {"element": "anemo", "region": "mondstadt",
                "buffs": {"res_shred": 0.40, "em": 150}},
    "Rosaria": {"element": "cryo", "region": "mondstadt",
                "enables": ["forward-melt", "reverse-melt"],
                "buffs": {"crit_rate": 0.10}},
    "Diona": {"element": "cryo", "region": "mondstadt",
              "enables": ["forward-melt", "reverse-melt"], "buffs": {"em": 0}},
}


def load_profiles() -> tuple[dict[str, Carry], dict[str, Support]]:
    """Charge le seed intégré, fusionné avec config/support_profiles.yaml."""
    override = load_yaml(project_root() / "config" / "support_profiles.yaml")
    carries_raw = {**_SEED_CARRIES, **(override.get("carries") or {})}
    supports_raw = {**_SEED_SUPPORTS, **(override.get("supports") or {})}
    carries = {n: Carry(name=n, **d) for n, d in carries_raw.items()}
    supports = {
        n: Support(name=n, **{**d, "enables": tuple(d.get("enables", []))})
        for n, d in supports_raw.items()
    }
    return carries, supports


# --------------------------------------------------------------------------- #
# Modèle de dégâts d'équipe
# --------------------------------------------------------------------------- #
def team_damage_index(
    carry: Carry, supports: list[Support], *, reaction: str | None,
    enemy_resistance: float = 0.10,
) -> dict[str, Any]:
    """Indice de dégâts relatif d'une équipe (carry + 3 supports)."""
    totals = {k: 0.0 for k in _BUFF_KEYS}
    totals["atk_pct"] = carry.atk_pct
    totals["atk_flat"] = carry.atk_flat
    totals["dmg_bonus"] = carry.dmg_bonus
    totals["crit_rate"] = carry.crit_rate
    totals["crit_dmg"] = carry.crit_dmg
    totals["em"] = carry.em
    for s in supports:
        for k, v in s.buffs.items():
            if k in totals:
                totals[k] += v

    atk = carry.base_atk * (1 + totals["atk_pct"]) + totals["atk_flat"]

    amp = 1.0
    if reaction and reaction in AMPLIFYING_BASE:
        amp = amplifying_multiplier(reaction=reaction, elemental_mastery=totals["em"]).amplifying_multiplier

    res = enemy_resistance - totals["res_shred"]
    hit = calculate_direct_hit(
        scaling=carry.scaling,
        scaling_stat=atk,
        damage_bonus=totals["dmg_bonus"],
        crit_rate=min(totals["crit_rate"], 1.0),
        crit_damage=totals["crit_dmg"],
        enemy_resistance=res,
        defense_reduction=min(max(totals["def_shred"], 0.0), 0.9),
        amplifying_reaction_multiplier=amp,
    )
    return {
        "index": round(hit.expected, 1),
        "atk": round(atk, 1),
        "amp_multiplier": round(amp, 3),
        "effective_resistance": round(res, 3),
        "totals": {k: round(v, 3) for k, v in totals.items()},
    }


def _is_valid(carry: Carry, trio: tuple[Support, ...], reaction: str | None) -> bool:
    members = [carry.region] + [s.region for s in trio]
    if carry.needs_natlan and sum(1 for r in members if r == "natlan") < carry.needs_natlan:
        return False
    if reaction and reaction in AMPLIFYING_BASE:
        enabler_el = _ENABLER_ELEMENT.get(reaction)
        if not any(reaction in s.enables for s in trio):
            return False
        # Exclut un support qui applique une aura tierce gênante (ni carry, ni activateur).
        for s in trio:
            if s.applies_aura and s.element not in (carry.element, enabler_el) \
                    and reaction not in s.enables:
                return False
    # Pas deux porteurs on-field.
    if any(s.on_field for s in trio):
        return False
    return True


def optimize(
    carry_name: str, *, reaction: str | None = None, pool: list[str] | None = None,
    top: int = 5, enemy_resistance: float = 0.10,
) -> dict[str, Any]:
    """Génère et classe les équipes valides du porteur par indice de dégâts."""
    carries, supports = load_profiles()
    if carry_name not in carries:
        raise KeyError(
            f"Porteur inconnu : {carry_name!r}. Connus : {', '.join(sorted(carries))}. "
            "Ajoute-le dans config/support_profiles.yaml."
        )
    carry = carries[carry_name]
    reaction = reaction or carry.reaction
    names = pool if pool is not None else list(supports)
    avail = [supports[n] for n in names if n in supports and n != carry_name]

    ranked: list[dict[str, Any]] = []
    for trio in combinations(avail, 3):
        if not _is_valid(carry, trio, reaction):
            continue
        res = team_damage_index(carry, list(trio), reaction=reaction,
                                enemy_resistance=enemy_resistance)
        ranked.append({
            "team": [carry.name] + sorted(s.name for s in trio),
            "supports": sorted(s.name for s in trio),
            **res,
        })
    ranked.sort(key=lambda r: -r["index"])

    best = ranked[0]["index"] if ranked else 0
    for r in ranked:
        r["relative"] = round(r["index"] / best, 4) if best else 0.0

    return {
        "carry": carry.name,
        "reaction": reaction,
        "pool_size": len(avail),
        "candidates_evaluated": len(ranked),
        "model": "analytique (plafond de buffs) — valider le top via gcsim",
        "top": ranked[:top],
    }


def owned_pool() -> list[str]:
    """Liste des supports possédés d'après le compte importé (data/account/current)."""
    import json
    path = account_subdir("current") / "characters.json"
    if not path.exists():
        return []
    chars = json.loads(path.read_text(encoding="utf-8")).get("characters", {})
    return sorted(chars.keys())
