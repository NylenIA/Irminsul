# Sources & vérification des formules du moteur

> Objectif (exigence Nylen) : **aucun calcul de DPS faux**. Chaque constante du
> moteur est ici sourcée et vérifiée. Référence primaire : **KQM TCL** (rang A),
> corroborée par une 2e source quand un doute existe. Toute valeur patch-dépendante
> porte sa version. Vérifié le **2026-07** (patch de référence à revalider à la veille).

Code : [`src/irminsul/reaction.py`](../../src/irminsul/reaction.py) (Python, source de vérité)
et son miroir [`packages/engine-client/src/reactions.ts`](../../packages/engine-client/src/reactions.ts),
parité prouvée par goldens croisés ([`tests/test_reaction_goldens_guard.py`](../../tests/test_reaction_goldens_guard.py) + `reactions.golden.test.ts`).

## Level multiplier
- **1446.85** au niveau 90. Source : [KQM TCL — Transformative](https://library.keqingmains.com/combat-mechanics/elemental-effects/transformative-reactions). ✅

## Bonus de Maîtrise (EM)
| Type | Formule | Source | État |
|---|---|---|---|
| Transformative | `16·EM/(EM+2000)` | KQM TCL | ✅ |
| Amplifiante | `2.78·EM/(EM+1400)` | KQM TCL — Amplifying | ✅ |
| Additive | `5·EM/(EM+1200)` | KQM TCL — Additive | ✅ |
| Lunaire | `6·EM/(EM+2000)` | KQM Lunar Reaction Guide (résolu sur 3 points publiés Icy Veins) | ✅ |

## Réactions transformatives (coefficient × Level Multiplier)
⚠️ **Patch 5.2** a buffé 4 réactions. Le moteur portait les valeurs **pré-5.2** (bug
corrigé le 2026-07). Confirmé par **3 sources concordantes** : KQM TCL, comparatif
[Game Rant 5.2](https://gamerant.com/genshin-impact-52-elemental-reaction-buff-damage-comparison-before-after/), et « SC = 1.5 × LevelMult ».

| Réaction | Pré-5.2 | **Actuel (moteur)** | Source |
|---|--:|--:|---|
| Electro-Charged | 1.2 | **2.0** | 5.2 buff |
| Overloaded | 2.0 | **2.75** | 5.2 buff |
| Superconduct | 0.5 | **1.5** | 5.2 buff |
| Shattered | 1.5 | **3.0** | 5.2 buff |
| Swirl | 0.6 | **0.6** | inchangé |
| Burning | 0.25 | **0.25** | inchangé |
| Bloom | 2.0 | **2.0** | inchangé |
| Hyperbloom | 3.0 | **3.0** | inchangé |
| Burgeon | 3.0 | **3.0** | inchangé |

Note EC : le coefficient est **par tick** ; le nombre de ticks (uptime) relève de la rotation, pas de la constante.
Garde anti-régression : `test_transformative_5_2_buffed_bases`.

## Réactions amplifiantes (multiplicateur du coup)
| Réaction | Base | Source |
|---|--:|---|
| Vaporize direct (Pyro→Hydro) | 2.0 | KQM ✅ |
| Vaporize inverse (Hydro→Pyro) | 1.5 | KQM ✅ |
| Melt direct (Cryo→Pyro) | 2.0 | KQM ✅ |
| Melt inverse (Pyro→Cryo) | 1.5 | KQM ✅ |

## Réactions additives (bonus ajouté à la base du coup)
| Réaction | Coef | Source |
|---|--:|---|
| Aggravate | 1.15 | KQM TCL — Additive ✅ |
| Spread | 1.25 | KQM TCL — Additive ✅ |

## Réactions lunaires (Luna I, dégâts propres avec crit)
| Réaction | Base | Élément | Source |
|---|--:|---|---|
| Lunar-Charged | 1.8 | Electro | KQM Lunar Reaction Guide ✅ |
| Lunar-Crystallize | 1.6 | Géo | KQM (corroboré wiki/game8) ✅ |
| Lunar-Bloom | — | Dendro | **EXCLU** : multiplicateur non confirmé par KQM (mécanique à cœurs) → rejet explicite, aucune valeur inventée |

## Stats d'artéfacts (main 5★ niveau 20)
[`packages/engine-client/src/artifact-stats.ts`](../../packages/engine-client/src/artifact-stats.ts) — table
exacte des mains 5★ niv20 (HP 4780, ATQ 311, HP%/ATQ% 46.6%, DEF% 58.3%, EM 187, ER% 51.8%,
CR% 31.1%, CD% 62.2%, DMG élémentaire 46.6%, DMG physique 58.3%, soin 35.9%). Source : valeurs
officielles/KQM. **Gate strict** : un artéfact hors 5★-niv20 → somme incomplète (TODO), jamais approximée.

## Sets d'artéfacts (bonus 2p/4p)
Les effets de set **ne sont pas codés en dur** dans le moteur : ils sont fournis par l'utilisateur
via `reaction_bonus` / `damage_bonus` (aperçu) ou par gcsim (simulation, sets natifs du binaire).
→ pas de risque de constante de set périmée côté moteur. À câbler explicitement si un jour on
calcule les sets nous-mêmes (nécessiterait un audit dédié par set + version).

## À revalider à chaque veille de patch
Coefficients de réaction (historique 5.2), valeurs de main stat (stables mais à surveiller),
nouvelles réactions (Lunar-Bloom en attente). **Process de veille : [PATCH_WATCH.md](PATCH_WATCH.md).**
