---
name: feedback-meta-research-rigor
description: Rigueur pour les questions "meilleure team / plafond méta" — raisonner les maths de buff, croiser les créateurs, ne pas parroter les agrégateurs
metadata:
  type: feedback
---

Pour toute question **« meilleure team / plafond de dégâts / BiS »**, ne pas se contenter d'agrégateurs (GameWith, Icy Veins, Game8) ni même du choix « pratique » de KQM : **raisonner la mécanique buff/debuff**, **croiser les créateurs de confiance du joueur** ([[reference-trusted-creators]] : Nokapt, AlexYukiii, Aiynao) et **exposer les désaccords de sources**. Distinguer **plafond** vs **consistance** vs **confort**.

**Why:** j'ai affirmé à tort que la meilleure team Mavuika était Citlali·**Xilonen**·Bennett et rétrogradé **Iansan** en « alternative C6 », en recopiant des snippets d'agrégateurs sans faire le calcul. Le joueur m'a corrigé **deux fois**. Cause racine = sourcing superficiel + absence de raisonnement DPS chiffré.

**Fait corrigé (vérifié par calcul) :** la team **plafond de dégâts** de Mavuika est **Mavuika · Citlali · Iansan · Bennett**. Mécanisme : Citlali apporte déjà le **shred de RES Pyro** (+ Cryo melt + bouclier + Fighting Spirit), donc le shred de Xilonen devient **redondant** ; empiler l'offensif d'Iansan (**+30 % ATK, +ATK plat, +25 % DMG élém.**) dépasse alors Xilonen. Xilonen reste le choix **consistance/empilement rapide de burst**, pas le plafond.

**How to apply:**
- Utiliser le nouvel outil `irminsul optimize-team <carry> [--reaction] [--owned-only]` (module `team_optimizer`, modèle analytique transparent) pour **calculer/classer** les teams ; un **test verrou** (`tests/test_team_optimizer.py::test_iansan_beats_xilonen_in_mavuika_citlali_team`) empêche de réintroduire l'erreur.
- **Étendre** la méta à d'autres persos en ajoutant porteurs/supports dans `config/support_profiles.yaml`, puis valider le top via **gcsim**.
- Toujours séparer plafond/consistance/confort et citer une source de rang A + le créateur du joueur ; ne jamais présenter une ligne d'agrégateur comme méta établie.
- Limite honnête : YouTube (chaînes des créateurs) n'est pas scrapable ici → demander les **liens de vidéos précises** si une valeur chiffrée d'un créateur est requise.
