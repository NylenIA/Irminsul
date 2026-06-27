# Journal — recherches & corrections (traçabilité)

Format par entrée : date · sujet · problème · cause racine · sources consultées ·
correction · fichiers · tests · résultat · limites.

---

## 2026-06-27 — Politique de recherche/rigueur + mode audit (centralisation)

- **Sujet** : durcir tout le projet pour qu'il cherche/vérifie avant d'agir, sépare
  les sources (A–D), gère les leaks, explicite la confiance et s'auto-audite.
- **Problème** : règles de rigueur dispersées et non exécutables ; pas de mode audit ;
  pas de garde-fous testés contre l'invention, l'obsolescence ou un leak présenté comme officiel.
- **Cause racine** : absence d'une **politique centrale** réutilisable et de **logique
  vérifiable** (les consignes vivaient seulement en prose dans CLAUDE.md).
- **Sources consultées** : CLAUDE.md existant, `docs/SKILLS_POLICY.md`, modules
  `leaks.py`/`status.py`/`config.py`, structure des agents/skills.
- **Correction** :
  - Politique centrale unique : `docs/RESEARCH_POLICY.md` (héritée par CLAUDE.md + 8 agents).
  - Module vérifiable `src/irminsul/research_policy.py` (déclenchement de recherche,
    fraîcheur, qualité/contradiction de sources, bannière leak, confiance, valeur
    inconnue non inventée, sûreté d'un skill externe).
  - Mode audit `src/irminsul/audit.py` + CLI `irminsul audit` + skill `/genshin-audit`.
  - 10 skills de recherche/vérification (deep-research, source-verifier, leak-auditor,
    fact-checker, consistency-checker, root-cause, regression-tester, version-checker,
    data-diff, answer-auditor).
  - Pointeur de politique ajouté dans CLAUDE.md et chaque sous-agent (héritage, sans duplication).
- **Fichiers** : voir le commit associé (`docs/RESEARCH_POLICY.md`, `src/irminsul/research_policy.py`,
  `src/irminsul/audit.py`, `src/irminsul/cli.py`, `.claude/agents/*.md`, `.claude/skills/*`,
  `tests/test_research_policy.py`, `tests/test_audit.py`, `CLAUDE.md`).
- **Tests** : `tests/test_research_policy.py` (14) + `tests/test_audit.py` (5) — couvrent
  déclenchement de recherche, obsolescence, contradiction, source sans date, repost,
  leak jamais officiel, confiance cohérente, refus de skill douteux, non-invention, audit.
- **Résultat** : `bash scripts/validate.sh` → Ruff OK + pytest OK (voir exécution).
- **Décision skills externes** : aucun skill tiers installé. Toutes les capacités requises
  (recherche/vérification/audit) sont couvertes par des skills **locaux** + Python standard ;
  installer un tiers ajouterait un risque supply-chain sans valeur nette (cf. `evaluate_external_skill`).
- **Limites restantes** : la conformité comportementale d'un agent (suivre la politique
  en pratique) reste partiellement non testable automatiquement ; l'audit ne lance pas
  encore les tests lui-même (utiliser `scripts/validate.sh`).
