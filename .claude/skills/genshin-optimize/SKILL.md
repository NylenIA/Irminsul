---
name: Genshin Team Optimizer
description: Calcule et classe les meilleures équipes d'un porteur (modèle de dégâts analytique), pour découvrir/valider des compositions méta.
argument-hint: "<porteur> [réaction] [--owned-only]"
---
Optimise la team du porteur : $ARGUMENTS

1. Lance `irminsul optimize-team <porteur> [--reaction forward-melt|forward-vaporize|…] [--owned-only] [--top N]` (PYTHONPATH=src). Le modèle (`irminsul.team_optimizer`) somme les buffs des supports dans la formule de dégâts (`calculate_direct_hit`) et **classe les équipes valides**.
2. **Avertis** que c'est un modèle **analytique** (plafond de buffs empilés) : il capture buffs/debuffs/réaction mais **pas** la vitesse de rotation, l'énergie fine ni l'uptime. → **Valide le top via `/genshin-dps` (gcsim)**.
3. Sépare **plafond** (cet outil) vs **consistance/confort** (jugement + gcsim). Croise avec les créateurs de confiance du joueur (Nokapt…) et **expose les désaccords**.
4. `--owned-only` restreint aux persos du compte importé. Pour étendre la méta (nouveau porteur/support ou valeurs d'un créateur), édite `config/support_profiles.yaml`.
5. Présente : équipe(s) classées + indice relatif, pourquoi (buffs dominants), et l'étape de validation gcsim.
