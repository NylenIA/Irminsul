---
name: product-vision-theorycrafter-app
description: Ce que l'utilisateur veut VRAIMENT d'Irminsul — un théorycrafteur dans une app (méta, DPS d'équipe, meilleure team) à partir de son compte
metadata:
  type: project
---

Vision produit centrale (exprimée le 2026-07-24, moment pivot) : l'utilisateur ne
veut pas « une app Genshin » générique. Il veut **le travail d'un théorycrafteur,
automatisé et personnalisé à son roster** :
- connaître la **méta du moment** ;
- calculer le **DPS théorique d'une équipe** (à partir de ses vrais builds) ;
- **construire la meilleure équipe** selon la méta (ou autour d'un perso choisi).

**Why:** l'implémentation actuelle (Tauri + Next + sidecar Python) l'a déçu :
« rien ne fonctionne bien », « pas intuitif », « design/ergonomie pas ouf », et
une page qui plante (« This page couldn't load »). Il envisage de **repartir de
zéro** et veut d'abord **discuter** pour que la vision soit comprise. Il regarde
du contenu sur les méthodes spec-driven (PRD + PLAN + DESIGN) pour cadrer avec
Claude Code → il veut une **spec produit d'abord, code ensuite**.

**Doc vivant de référence : `docs/VISION.md`** (vision complète, design, réalité
de terrain, journal des décisions) — le lire/mettre à jour à chaque session sur ce
sujet. Décisions actées le 2026-07-24 : **vrai app NATIVE** (pas web/webview ; Tauri
abandonné ; Flutter recommandé), **gratuit**, code+build **dans le cloud** (GitHub
Codespaces + Actions) pour libérer le disque de l'utilisateur, moteur **gcsim**,
design **dashboard sombre glassmorphism (réf Helios) + touches Genshin** (mélange
gamer/pro). Scope élargi souhaité (scanner OCR, optimizer type Genshin Optimizer
boosté IA, carte Teyvat, fiches persos+matériaux) MAIS réalité de terrain : cœur =
theorycrafter ; import compte via fichier GOOD existant (pas d'OCR maison) ; carte
non recréée ; « IA » à définir (coût LLM vs gratuit).

**How to apply:** recentrer TOUT sur cette boucle cœur (compte → meilleures teams
+ DPS). Le « cerveau » (moteur dégâts/réactions/gcsim, import GOOD, tests pytest)
est la partie de valeur à **préserver/porter** ; c'est le PRODUIT/UX qui est à
refonder. Rester honnête sur le scope : une brique excellente à la fois, ne pas
tout construire d'un coup (sinon on refait le crash). Passer en « natif » ne réglerait ni le
« pas intuitif » ni le « meilleure team » — ce sont des problèmes produit. Voir
[[account-level-meta]] (il est calé méta, exige de la rigueur) et
[[meta-research-rigor]] (buff-math, croiser créateurs). Lié à [[roster-goals]].
