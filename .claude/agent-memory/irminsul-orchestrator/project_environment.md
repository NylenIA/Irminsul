---
name: project-environment
description: Contraintes machine d'installation Irminsul AI (à revérifier, peut changer)
metadata:
  type: project
---

État de la machine d'install au 2026-06-25 (à **revérifier** avant de s'en servir) :

- **Python 3.14.3** présent ; **git** présent.
- **`uv` ABSENT** et **Node/`npm` ABSENT**. Le `bootstrap.ps1` d'origine échouait donc (il exigeait `npm`/`claude` et `uv`).
- Installation réalisée en repli : `.venv` créé via `python -m venv` + `pip install -e ".[dev]"`. Le serveur MCP, le CLI et les 12 tests tournent sous Python 3.14.

**Why :** le chemin d'install « officiel » (uv + tâche planifiée Windows) n'est pas exécutable tel quel sur cette machine ; un repli pip a été ajouté au bootstrap.

**How to apply :** avant de supposer `uv`/`node` disponibles, vérifier (`uv --version`, `node --version`). Pour valider rapidement le projet, utiliser `./.venv/Scripts/python.exe -m pytest -q` et `... -m irminsul.cli doctor`.
