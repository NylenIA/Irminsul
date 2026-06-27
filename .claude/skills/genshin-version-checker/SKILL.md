---
name: Genshin Version Checker
description: Détermine la version live actuelle de Genshin (et la version d'un contenu) avant toute conclusion datée.
argument-hint: "<contenu ou question>"
---
Vérifie la version : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §2.
1. Détermine la **version live actuelle** (sources officielles HoYoverse + KQM GINews ; recouper la date).
2. Pour le contenu visé : précise s'il est **LIVE**, **bêta/leak**, ou **historique** (patch d'origine).
3. Signale toute donnée dont la version ne correspond pas à la version live (guide obsolète, kit bêta).
4. Pour un sujet technique (lib/API/outil) : version installée vs récente, changelog, breaking changes (§8).
5. Conclus : version live = X (date, source), statut du contenu, et risque d'obsolescence.
