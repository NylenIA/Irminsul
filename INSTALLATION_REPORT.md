# Rapport d'installation — Irminsul AI

**Date :** 2026-06-26
**Statut :** ✅ Installation fonctionnelle et vérifiée de bout en bout.

---

## 1. Emplacement final du projet

```
C:\Users\akuon\IA Genshin\Irminsul-AI-Claude-Code
```

Source : `E:\Download\Irminsul-AI-Claude-Code.zip` (archive du projet Irminsul).
L'archive `E:\Download\Agent_Genshin_Claude.zip` est un **projet différent et
antérieur** (« Agent_Genshin_Claude ») et n'a **pas** été utilisée.

> Le projet était déjà extrait à cet emplacement (build 2026-06-25). Plutôt que de
> tout réextraire (ce qui aurait écrasé des correctifs locaux plus récents que le
> zip), j'ai **vérifié, corrigé et finalisé l'install en place**. Aucune suppression
> destructrice n'a été nécessaire.

---

## 2. Versions utilisées

| Composant | Version | Remarque |
|---|---|---|
| Python | 3.14.3 | ≥ 3.11 requis ✅ |
| Git | 2.54.0.windows.1 | ✅ |
| gcsim | v2.43.3 | retéléchargé (binaire d'origine corrompu) |
| Projet `irminsul-ai` | 0.1.0 | installé en editable dans `.venv` |
| uv | **absent** | repli automatique sur `venv` + `pip` |
| Node.js / npm | **absent** | non requis pour le cœur ; conseillé pour installer Claude Code |

Environnement virtuel : `.venv\` (créé via `python -m venv`).

---

## 3. Dépendances installées (dans `.venv`)

**Runtime :** httpx 0.28.1 · mcp 1.28.0 · platformdirs 4.10.0 · pydantic 2.13.4 ·
PyYAML 6.0.3 · RapidFuzz 3.14.5 · rich 14.3.4 · tenacity 9.1.4 · typer 0.26.7.

**Dev :** pytest 9.1.1 · ruff 0.15.20.

> `pyproject.toml` épinglait `pytest>=8,<9` alors que **9.1.1** était installé
> (incohérence qui aurait fait rétrograder pytest à la prochaine install). Pins
> réalignés (`pytest>=8,<10`, `ruff>=0.6,<2`) et **`pytest-asyncio` retiré** car
> non utilisé (les tests async passent par `asyncio.run`). `pip install -e ".[dev]"`
> reconcilie l'environnement sans aucun téléchargement tiers.

---

## 4. Skills externes (find-skills / skills.sh)

Aucun skill externe installé. L'outil `find-skills`/`skills.sh` **n'était pas exposé**
dans cette session d'orchestration. Conformément à `docs/SKILLS_POLICY.md`, les
**skills locaux du projet ont été conservés** : ils couvrent déjà les 12 commandes
Genshin (`/genshin-*`) et un skill externe générique aurait été **redondant** sans
bénéfice fiable. Recommandation : si tu veux des skills génériques (tests, revue de
code, automatisation Git), audite-les un par un (source, réputation, permissions,
absence d'exfiltration) avant adoption — voir `scripts\skills-audit.ps1`.

---

## 5. Modifications réalisées

**Corrections (bugs/robustesse) :**
1. **Launcher MCP (critique)** — `scripts/mcp_launch.py` utilisait `os.execv`, qui
   **casse l'héritage des pipes stdio sous Windows** : le client MCP (Claude Code)
   perdait la connexion (handshake `initialize` → « Connection closed »). Remplacé
   par un sous-processus héritant des flux. **C'était le blocage principal** qui
   aurait empêché Claude Code d'utiliser le serveur.
2. **gcsim** — l'exécutable présent (`gcsim_windows_amd64.exe`, exactement 31,0 Mio)
   était **tronqué/corrompu** (erreur Windows 193). Retéléchargé en v2.43.3 (35,5 Mo,
   `-version` OK) et renommé `gcsim.exe`. `gcsim_path()` accepte désormais aussi un
   binaire au nom non canonique (repli par glob).
3. **Indexeur runaway** — `config/sources.yaml` indexait `genshin-db/src/**/*.json`
   = **119 587 fichiers** (12 langues × tous objets, dont cartes TCG). Restreint à
   l'anglais combat-utile (**2 480** fichiers). `source_sync._iter_documents`
   refactoré pour **globber directement les includes** (au lieu de parcourir tout
   l'arbre) + **plafond par source** (`IRMINSUL_MAX_FILES_PER_SOURCE`). Index final =
   **6 410 documents** en ~50 s.
4. **Encodage console** — la sortie CLI s'affichait avec des `�` (Python < 3.15 sur
   Windows). Sortie forcée en UTF-8 dans `cli.py` ; `PYTHONUTF8`/`PYTHONIOENCODING`
   ajoutés à l'environnement du serveur MCP (`.mcp.json`).
5. **Ruff** linta du code tiers synchronisé (`data/sources/...`). Ajout de
   `extend-exclude = ["data", "tools/bin", ".venv"]`.

**Sécurité / données personnelles :**
6. `.gitignore` durci : `profiles/player.yaml`, exports GOOD, `data/irminsul.db-*`,
   `.claude/settings.local.json`.
7. Ajout de `profiles/player.example.yaml` (modèle sans UID).
8. **Git initialisé** + `.gitattributes` (fins de ligne portables). Contrôle effectué
   avant commit : **aucune** donnée perso (UID, `.env`, cache Enka, binaires) suivie.

**Améliorations testables :**
9. `config.tier_rank()` + `config.ranked_sources()` : classement des sources rendu
   explicite et vérifiable (S officiel > A theorycraft/sim > B données > …).

**Tests ajoutés** (12 → 36) :
GOOD invalide (mauvais format, JSON cassé, fichier absent) · validation UID Enka
(7 cas invalides, sans réseau) · classement des sources · serveur MCP (10 outils +
handshake stdio du launcher) · source/index indisponible (dégradation propre) ·
gcsim (binaire absent, config absente, **run réel reproductible**).

---

## 6. Tests exécutés et résultats

| Vérification | Commande | Résultat |
|---|---|---|
| Suite unitaire complète | `python -m pytest -q` | **36 passed** |
| Lint | `python -m ruff check .` | **All checks passed** |
| Auto-diagnostic | `irminsul doctor` | **5/5 OK** (Python, gcsim, index 6410 docs, sources 4/4, fraîcheur) |
| Serveur MCP (direct) | JSON-RPC stdio | initialize OK · 10 outils · appels d'outils OK |
| Serveur MCP (launcher `.mcp.json`) | JSON-RPC stdio | initialize OK · 10 outils · `calculate_amplifying_multiplier` & `search_knowledge` OK |
| Calcul DPS coup isolé | tool `calculate_direct_hit` | OK |
| Réactions | `calculate_amplifying/transformative` | OK (EM 200 → ×2.695 vaporize) |
| gcsim simulation réelle | `simulations\smoke-test.txt` | rc=0, DPS parsé |
| Import GOOD | tests + tool `inspect_good_export` | OK |
| Recherche locale | tool `search_knowledge` | renvoie des docs KQM tier A |
| Source indisponible | test dédié | renvoie `[]` au lieu d'inventer |

---

## 7. Avertissements / limites restantes

- **gcsim dépend du réseau** pour son (re)téléchargement et **de la version** pour la
  syntaxe des configs : `simulations\smoke-test.txt` est validé pour la v2.43.x.
- **Node/npm absents** : sans eux, l'installation de Claude Code via npm n'est pas
  possible depuis ce projet ; le cœur Irminsul (MCP, CLI, tests) fonctionne sans.
- **`uv` absent** : `bootstrap.ps1` bascule automatiquement sur `venv` + `pip`.
- **Index** : volontairement limité à genshin-db anglais (combat) pour rester
  pertinent et rapide ; les autres langues restent sur disque mais non indexées.
- **`.env.example`** est protégé en lecture par `Read(./.env.*)` dans
  `settings.json` (choix prudent). Pour ajouter `IRMINSUL_MAX_FILES_PER_SOURCE`,
  édite-le manuellement ; valeur par défaut = 20000.
- La **tâche planifiée** quotidienne n'est **pas** installée (aucune automatisation
  silencieuse). Activation explicite via `bootstrap.ps1`, retrait via
  `UNINSTALL_IRMINSUL.bat`.

---

## 8. Architecture vérifiée

**8 agents détectés par Claude Code :** `irminsul-orchestrator` + `theorycrafter`,
`dps-analyst`, `account-optimizer`, `live-data-researcher`, `lore-archivist`,
`leak-analyst`, `source-auditor`.

**12 commandes Genshin** (skills sous `.claude/skills/`) : `genshin-account`,
`genshin-import-good`, `genshin-team`, `genshin-dps`, `genshin-build`, `genshin-meta`,
`genshin-lore`, `genshin-leaks`, `genshin-verify`, `genshin-update`,
`genshin-rotation`, `genshin-pulls`.

**10 outils MCP :** `irminsul_status`, `refresh_knowledge`, `search_knowledge`,
`calculate_direct_hit`, `calculate_transformative_reaction`,
`calculate_amplifying_multiplier`, `score_leak`, `import_enka_showcase`,
`inspect_good_export`, `run_gcsim`.

**Sources** (`config/sources.yaml`) hiérarchisées par tier : officiel HoYoverse (S) >
KQM/gcsim (A) > genshin-db/Genshin Optimizer/Enka (B). Séparation stricte
OFFICIEL/LIVE/THÉORYCRAFT/SIMULATION/LEAK/SPÉCULATION conservée.

---

## 9. Procédure de lancement

1. Double-clic sur **`START_IRMINSUL.bat`** (ou `claude` dans le dossier projet).
2. Accepter une fois le serveur MCP **« irminsul »**.
3. L'agent **`irminsul-orchestrator`** est actif. Première commande utile :
   `/genshin-account <ton UID>`.

Diagnostic à tout moment : `.venv\Scripts\python.exe -m irminsul.cli doctor`.
Mise à jour des données : `UPDATE_IRMINSUL.bat`. Guide complet :
**`DEMARRAGE_RAPIDE.md`**.
