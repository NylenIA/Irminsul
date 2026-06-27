# Politique de recherche, vérification et rigueur — Irminsul AI

**Source unique de vérité.** Tous les agents et skills héritent de cette politique
(la référencer, ne pas la recopier). CLAUDE.md la rend obligatoire ; chaque sous-agent
peut ajouter des règles propres à son domaine sans la contredire.

Outils d'appui : module `irminsul.research_policy` (logique vérifiable + testée),
`irminsul.audit` / `irminsul audit` (audit projet), `score_leak`, `system_status`.

---

## 1. Principe fondamental — chercher avant d'agir
La mémoire interne n'est **jamais** suffisante pour une information : récente,
susceptible d'avoir changé, liée à une version/patch, à la méta, à un leak, à une
bibliothèque/API, incertaine, contradictoire, difficile à vérifier, absente de la
base locale, ou non sûre à 100 %.

Dans ces cas : **rechercher avant de répondre, modifier du code, analyser ou décider.**
Ne jamais inventer, compléter au hasard, extrapoler sans le dire, ni présenter une
hypothèse/leak comme un fait. Si une donnée reste inconnue → la marquer
`Non vérifiable actuellement`, pas une valeur inventée.

Ne pas bloquer inutilement : pour un fait **stable et déjà validé localement**, ne pas
sur-rechercher. Répondre avec ce qui est vérifiable, signaler les limites.

## 2. Processus de recherche approfondie
1. définir la question ; 2. lister les infos nécessaires ; 3. vérifier la **version
live** concernée (`irminsul status`) ; 4. sources primaires ; 5. sources secondaires
fiables ; 6. comparer les **dates** ; 7. comparer les **versions** ; 8. errata/corrections ;
9. contradictions ; 10. comprendre *pourquoi* les sources divergent ; 11. recouper
≥ 2 sources indépendantes ; 12. ne conclure qu'après réduction suffisante de l'incertitude.
→ Pour un sujet important, **plusieurs requêtes différentes**, pas le premier résultat.

## 3. Hiérarchie des sources (A > B > C > D)
- **A — Primaires** : HoYoverse officiel, notes de version, in-game, version live, dépôts
  officiels, doc officielle d'API/bibliothèque, code source de l'outil, publication d'origine.
- **B — Techniques reconnues** : KQM, gcsim, Genshin Optimizer, Enka.Network, bases
  maintenues, theorycraft reproductible (configs disponibles).
- **C — Communautaires** : guides, discussions, vidéos avec méthodologie, feuilles de
  calcul, analyses indépendantes. **Jamais vérité absolue sans recoupement.**
- **D — Leaks / non confirmé** : datamining, bêta, captures, témoignages, rumeurs,
  reposts, traductions non officielles. **Toujours séparés du LIVE/OFFICIEL.**

Une source **secondaire ne vaut pas une primaire**. Un **repost** vaut moins que la
source d'origine. Une source **sans date** est pénalisée.

## 4. Leaks (niveau D)
Bannière obligatoire sur toute réponse contenant un leak :

> ⚠️ LEAK NON CONFIRMÉ — ces informations peuvent changer, être incomplètes ou être fausses.

Scorer **chaque** leak avec `score_leak` (provenance, preuve, corroboration, track record,
précision, stade). Préciser : date du leak, version supposée, niveau de confiance, éléments
confirmés/incertains, ce qui peut encore changer. Catégories : très probable / crédible /
incertain / rumeur faible / spéculation / réfuté / devenu officiel. **La réputation seule
ne suffit jamais** : un bon leaker se trompe, un inconnu peut viser juste.

## 5. Vérification finale avant réponse importante
Chercher : erreurs factuelles, incohérences internes, contradictions entre sections,
données anciennes, confusion live/bêta, confusion leak/officiel, erreurs de calcul, unités,
noms, niveaux de talents, multiplicateurs, buffs oubliés/dupliqués, RES oubliée, mauvaise
formule de DEF, hypothèses de rotation irréalistes, énergie irréaliste, temps d'animation,
traductions, sources mortes, secondaire prise pour primaire, affirmations sans preuve,
interprétations présentées comme faits.
**Cohérence transversale** : toute la réponse parle de la même version, constellation, arme,
raffinement, niveau, talent, set, cible, RES, nombre d'ennemis, durée de rotation, hypothèse.

## 6. Comprendre avant de corriger (cause racine)
Pour une erreur : quoi / où / depuis quand / cause / fichiers concernés / erreurs similaires /
risque de régression / comment l'empêcher de revenir. Chercher la **cause racine** (cache
ancien, mauvaise priorité de source, parsing, arrondi prématuré, formule incomplète, prompt
ambigu, validation absente, mauvais mapping de noms, live mélangé au leak, MAJ partielle,
dépendance obsolète, test manquant, conversion, doublon de buff, hypothèse cachée).

## 7. Correction définitive (pas de patch cosmétique)
Idéalement : corriger code/données **+** prompt concerné **+** doc **+** validation **+**
message d'erreur clair **+** test de non-régression **+** vérifier les fichiers similaires et
modules dépendants **+** relancer les tests **+** journaliser (cf. §10).
Interdits : `try/except` trop large qui masque l'erreur, ignorer silencieusement une donnée
invalide, remplacer une valeur inconnue par une valeur inventée.

## 8. Sujets techniques (lib / API / outil)
Vérifier : doc officielle actuelle, version installée, version récente, changelog, breaking
changes, problèmes connus, dépôt, issues pertinentes, compat Windows, licence, sécurité,
dernière maintenance. Ne pas proposer une commande/API obsolète sans le signaler.

## 9. Niveau de confiance (toujours explicite)
`Confiance élevée` (plusieurs primaires concordent) · `Confiance moyenne` (une secondaire,
ou recoupement partiel) · `Confiance faible` (bêta, source unique, ancien) ·
`Non vérifiable actuellement` (source d'origine introuvable, données incomplètes, conflit
non résolu). Toujours dire **pourquoi** en une ligne.

### Format de réponse recommandé (sujets nécessitant recherche)
Conclusion · Version concernée (live/bêta) · Données vérifiées · Hypothèses · Sources
(avec date + type) · Contradictions détectées · Leaks (section séparée si besoin) ·
Niveau de confiance · Limites.

## 10. Traçabilité
Toute correction importante → entrée dans `CHANGELOG_RESEARCH_AND_FIXES.md` (date, sujet,
problème, cause racine, sources consultées, correction, fichiers, tests ajoutés, résultat,
limites restantes).

## 11. Audit
`irminsul audit` / `/genshin-audit` vérifie architecture, agents, skills, MCP, dépendances,
sources, caches, MAJ, import GOOD, Enka, gcsim, DPS, leaks, tests, docs, sécurité,
confidentialité, compat Windows, cohérence des prompts. Sévérités : CRITIQUE / IMPORTANT /
INCOHÉRENCE / RISQUE / OBSOLÈTE / RECOMMANDATION / OK.

## 12. Skills externes
Avant d'installer (find-skills / skills.sh) : inspecter contenu, dépôt, auteur, permissions,
commandes exécutées, dépendances, comportements suspects, exfiltration de données, code
inutile, valeur réelle. Ne pas installer par popularité ni en double, ni utiliser en boîte
noire. Si aucun skill fiable ne répond → **créer un skill local dédié**. Évaluer un manifeste
via `research_policy.evaluate_external_skill`.
