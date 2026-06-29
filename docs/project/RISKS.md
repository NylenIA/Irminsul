# RISKS

| Risque | Impact | Mitigation |
|---|---|---|
| ~~Build Tauri local impossible (MSVC absent)~~ — **RÉSOLU 2026-06-28** | — | VS 2022 Build Tools (VCTools) installés ; `cargo check` OK ; **build release local produit** `irminsul.exe` + installeurs **MSI/NSIS**. CI `desktop.yml` reste la validation reproductible. |
| Règles par chemin non chargées pour une Q&A pure (sans toucher au code) | perte de contexte domaine | garder l'essentiel universel dans CLAUDE.md ; détail procédural dans skills invocables |
| 30 skills → catalogue large | coût si tout envoyé | chargement à la demande (descriptions courtes) ; recherche dynamique d'outils côté app (§10) |
| Données perso (UID/pseudo, GOOD) | exposition | `data/account/` + `.claude/agent-memory/` gitignorés. **RÉSOLU 2026-06-29** : le vrai UID (présent dans un message de commit) **retiré** par réécriture des messages limitée à `feat` (`filter-branch` + `--force-with-lease`, arbre identique vérifié) ; purgé local + distant ; `main`/tags intacts. Repo **privé**. |
| Contre-revues Codex (gates de fusion) | fusion bloquée | **R2 ✅ + R3 ✅** (changes-required → corrigés) ; **R4 (talents) à faire**. Fusion interdite avant R4 OK + 0 défaut critique/élevé + CI verte + app packagée. |
| Incident : suppression `engine.ts` hors mission (2026-06-29) | perte de fichier | **mitigé** : `codexSandbox=read-only` (Codex ne peut plus écrire) ; test `test_repo_integrity.py` (détecte fichier critique manquant) ; **scheduler Duo désactivé** jusqu'à isolation confirmée. Détail : `docs/reviews/INCIDENT_engine_ts.md`. |
| Prompt caching app non finalisable sans gateway | gain partiel en Phase 0 | spécifié/préparé en Phase 0, finalisé en Phase 5 |
| Comptage de tokens = estimation locale (~chars/4) | imprécision | utiliser l'endpoint officiel de comptage avant opérations proches d'une limite (Phase 5) |
| Test handshake MCP stdio sensible à l'OS (0 outil sur ubuntu) | faux rouge CI | `skipif` Windows-only (régression `os.execv` propre à Windows) ; contrat outils couvert par un test unitaire toutes plateformes |
| Sidecar onefile : surcoût d'extraction par appel | latence légère | acceptable pour ops compte/calcul ponctuelles ; mode serveur long-vécu envisageable si besoin (mesurer avant d'optimiser) |
| Stats de base **perso** = OK ; **arme** encore absente | ATQ finale incomplète | perso fait (`basestats`) ; **T2 = stats de base d'arme** (extraction `curve/weapons.json`+`stats/weapons.json`) → `final_stats.atk.complete`. En attendant, ATQ saisie manuellement (étiquetée), `complete=false`. Ne jamais approximer. |
| Dérive de version (coefficients/valeurs qui changent au patch) | données obsolètes | résoudre la version live au moment de la recherche ; ne pas graver « actuel » ; statut+date+source par mécanique dans le registre. |
