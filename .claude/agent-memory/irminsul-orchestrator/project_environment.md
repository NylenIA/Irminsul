---
name: project-environment
description: Contraintes machine d'installation Irminsul AI (revérifié 2026-06-26)
metadata:
  type: project
---

État de la machine d'install, **revérifié le 2026-06-26** :

- **Python 3.14.3** présent ; **git 2.54** présent. Dépôt Git désormais **initialisé**
  dans le projet (1er commit fait ; `player.yaml`, exports GOOD et `settings.local.json`
  gitignorés).
- **`uv` ABSENT** et **Node/`npm` ABSENT** (toujours). Le chemin d'install « officiel »
  (uv + npm/Claude Code) n'est pas exécutable tel quel ; `bootstrap.ps1` bascule sur
  `python -m venv` + `pip install -e ".[dev]"`.
- **gcsim v2.43.3** installé et fonctionnel (`tools/bin/gcsim.exe`). La tâche planifiée
  Windows `IrminsulDailyUpdate` n'est **pas** installée par défaut.
- Validation : **36 tests OK**, ruff propre, serveur MCP 10 outils (handshake stdio
  vérifié), index local = ~6410 documents.

**Why :** ces contraintes (uv/node absents) reviennent à chaque session et changent le
chemin d'install ; il faut les vérifier avant de supposer un outil disponible.

**How to apply :** avant de supposer `uv`/`node`, vérifier (`uv --version`,
`node --version`). Pour valider vite : `./.venv/Scripts/python.exe -m pytest -q` et
`... -m irminsul.cli doctor`. Voir [[user-profile]] et [[feedback-proactive-improvements]].
