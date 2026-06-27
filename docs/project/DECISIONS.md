# DECISIONS

- **Politique centrale unique** : `docs/RESEARCH_POLICY.md` (héritée). On dédoublonne au lieu de recopier.
- **CLAUDE.md = index lean** : architecture/commandes/priorités/politique-contexte + liens. Détail domaine → `.claude/rules/` (chargées par chemin) et skills à la demande.
- **Infra déterministe en scripts**, pas en prose modèle : mesure, index, compression de logs, projection JSON.
- **Logs hors contexte** : `.irminsul/logs/` ; au modèle = exit code réel + erreurs uniques + résumé + chemin. Jamais de pipe qui masque le code de sortie.
- **Gros fichiers jamais injectés** : GOOD/SQLite/gcsim/builds → `peek_json.py` / extraction ciblée.
- **Budgets souples** (`config/token-budgets.json`) : jamais de réduction de qualité/test/source.
- **Modèle/effort adaptatifs** : éco (exploration) → équilibré (dev) → avancé (archi/sécurité/theorycraft/debug) ; monter si risque.
- **Skills** : on n'a pas supprimé les commandes Genshin existantes (chargées à la demande, coût permanent nul) ; on ajoute seulement les capacités orthogonales utiles. Le prompt caching réel est **préparé** (préfixe stable tools→system→messages) et sera finalisé avec la gateway Claude (Phase 5).
