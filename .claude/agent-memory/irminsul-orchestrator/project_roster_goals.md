---
name: project-roster-goals
description: Roster et objectifs connus du joueur (Mavuika, Nicole, projets Sandrone) — à revérifier via Enka/GOOD
metadata:
  type: project
---

**UID Enka : <UID>** (pseudo *<PSEUDO>*, AR60, WL9, Abysse 12-3 36★, Stygian dégagé). Importé le 2026-06-26 (le MCP `import_enka_showcase` échoue sur un redirect 308 → contourner via `curl https://enka.network/api/uid/<uid>` sans slash final).

Objectifs déclarés :
- **Mavuika** C0, arme **Wolf's Gravestone R1 (lvl80)**, 4p Obsidian Codex. Vise peut-être son **R1 signature** (*A Thousand Blazing Suns*). Pas de Citlali.
- Prévoit de pull **Sandrone** (5★ Cryo/claymore, sortie 6.7 le **2026-07-01**) → team de planification (LEAK, score E).
- A précisé : **a Furina, pas d'Escoffier** ; BiS Mavuika selon lui = Mavuika/Citlali/Iansan/Bennett.

**BOX COMPLÈTE vérifiée via GOOD réel** (`genshinData_GOOD_2026_07_24_16_44.json`,
Inventory Kamera v3, importé dans l'app Flutter le 2026-07-24) : **85 persos,
292 armes, 578 artefacts**. Faits saillants :
- Mavuika C0 Nv90 · Raiden C0 Nv90 · Yelan C0 Nv90 · Bennett **C6** Nv80 ·
  Xingqiu **C6** Nv80 · Furina C0 Nv80 · Nahida C0 Nv80 · Xilonen C0 Nv80 ·
  **Iansan C0 Nv40 (à monter)**.
- **N'a PAS : Citlali, Zhongli** (les suggestions « en attendant » de l'app
  s'appuient dessus).
- ER réelles calculées : Bennett ~158 % (117,5 artefacts + Skyward Blade Nv60),
  Xingqiu ~184 % (133,6 + Sacrificial Sword Nv70).

Builds réels notables (vitrine, 2026-06-26) :
- **Xilonen** ⭐ excellente : Peak Patrol Song, 4p Scroll Cinder City, DEF 3517, ER 145 %.
- **Furina** : 4p Golden Troupe, HP 31k, ER 184 %, mais **arme au niveau 1** (gros manque à gagner).
- **Nicole** C0R1 : Angelos' Heptades, 4p Celestial Gift, ATK 2951, ER 175 %.
- Autres unités possédées : **Skirk, Lohen, Flins, Ineffa, Columbina, Durin, Zibai, Linnea** (DPS/supports Cryo/Électro/Hydro/Hexerei/Lunar — beaucoup hors training, revérifier via web).

**Import GOOD complet (Inventory Kamera v1.4.3, snapshot 2026-06-26, SHA `f42d7054…`)** : 83 persos, 350 armes, 397 artéfacts, 529 matériaux. Pipeline `irminsul.account` → vérité normalisée dans `data/account/current/*.json` (gitignored). Rapports : `data/account/reports/` + `data/account/recommendations/initial-account-analysis.md`.
- **Possédés confirmés** : YaeMiko, Ayaka, HuTao, Raiden, Skirk (tous lvl90), Neuvillette (lvl70, **sous-investi à fort potentiel**), Nahida, Kazuha (R5 Iron Sting), **Bennett C6**, Furina, Xilonen, Lyney, Sucrose C6, Fischl C6, Columbina C2, Lohen, Flins, Ineffa.
- **NON possédés** (ne jamais supposer) : **Citlali, Xiangling, Mualani, Kinich, Chasca, Clorinde, Arlecchino, Navia, Wriothesley, Nilou, Escoffier**.
- **Pièges build scannés** : **Iansan lvl40 T1/1/1** (pas prête, mais Calamity Queller dessus) ; Furina/Shenhe/Yelan/Diona = **arme lvl1** ; Ayaka/HuTao/Bennett/Nahida = armes sous-montées. **Goulot = XP perso/Mora** (Hero's Wit 1, Mora 224k) ; 16 Couronnes dispo.
- `Traveler` = `unresolvedCharacter` (Amenoma + 5 artéfacts) → exclu des recos.

**Meta Mavuika (corrigé, cf. [[feedback-meta-research-rigor]]) :** team **plafond du jeu = Mavuika · Citlali · Iansan · Bennett** (pas Xilonen ; Citlali shred déjà la RES). Sur CE compte : Citlali non possédée + Iansan lvl40 → meilleure team **réelle** = **Mavuika · Xilonen · Furina · Bennett (Vape)**. Pour Melt sans Citlali/Escoffier : activateur Cryo possédé le moins mauvais = **Rosaria** (à monter).

**Why:** ces builds réels conditionnent les recos.

**How to apply:** réimporter l'Enka avant de conclure (les builds évoluent) ; gros leviers identifiés = monter l'arme de Furina (lvl1→90) et rééquilibrer le crit de Mavuika (~63 % CR en combat pour 198 % CD). Bennett/Iansan supposés possédés mais non affichés → confirmer. Sandrone = LEAK jusqu'au 2026-07-01. Lié à [[project-environment]], [[feedback-account-level-meta]], [[reference-trusted-creators]].
