---
name: feedback-proactive-improvements
description: Sur Irminsul AI, accompagner l'exécution de corrections de bugs et d'idées de fonctionnalités
metadata:
  type: feedback
---

Quand l'utilisateur confie une tâche sur le projet (« installe », « regarde ça »), livrer **3 choses** : l'exécution demandée, les **corrections de bugs/robustesse** trouvées en chemin, et des **idées de nouvelles fonctionnalités**.

**Why :** lors de l'installation du 2026-06-25 il a explicitement demandé « apporte des améliorations… corrections de bug… et de nouvelles idées ». C'est sa façon de collaborer sur ce projet personnel qu'il fait évoluer.

**How to apply :** rester focalisé et à faible risque (tests + ruff doivent rester verts), montrer les hypothèses, proposer des alternatives moins coûteuses. Ne pas tout déléguer aux sous-agents sans qu'il le demande. Voir [[user-profile]].

**Limite fixée le 2026-07-24 :** « fais bien attention aux erreurs, et si tu vois
des améliorations à faire fais-le **sauf pour les gros changements : demande-moi
avant** ». Donc : corrections/polish/qualité de conseil → j'y vais ; refonte
d'archi, changement de stack ou de périmètre produit → je demande d'abord
(cf. [[discuss-before-big-rebuilds]]).

**Méthode QA qui a prouvé sa valeur (app Flutter) :** avant chaque build,
rejouer la logique Dart en Python contre le **GOOD réel** de l'utilisateur
(`irminsul_app/tool/simulate_match.py`, `diag_box.py`). Ça a révélé 3 mauvais
conseils invisibles en lecture de code (remplaçant Nv1 proposé alors qu'un Nv80
existait, alerte ER sur un perso sans artefacts, arme Nv1 non détectée).
Simuler sur données réelles > relire le code.
