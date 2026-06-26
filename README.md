# Irminsul AI — Agent Genshin Impact pour Claude Code

Irminsul AI transforme un projet Claude Code en assistant Genshin spécialisé : theorycraft, équipes, calculs DPS, optimisation de compte, lore, veille meta et analyse prudente des leaks.

## Ce que le projet fournit

- Un agent principal Claude Code et 7 sous-agents spécialisés.
- Des skills `/genshin-*` prêts à invoquer.
- Un serveur MCP local (10 outils) : recherche, calcul de dégâts, calcul de réactions transformatives et amplifiantes, score de fiabilité des leaks, import Enka et exécution gcsim.
- Une base locale indexée à partir de sources publiques reconnues.
- Une séparation stricte entre informations officielles, données live, theorycraft, simulations, leaks et spéculations.
- Une mise à jour quotidienne locale sous Windows après l'installation.

## Installation rapide — Windows

Prérequis : Python 3.11+, Git, Node.js/npm, Claude Code.

Double-clique sur `INSTALLER_IRMINSUL.bat`.

Ou depuis PowerShell :

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap.ps1
```

Le script :

1. installe `uv` si nécessaire (repli automatique sur `venv` + `pip` si `uv` reste indisponible) ;
2. installe les dépendances Python ;
3. télécharge la dernière version compatible de gcsim quand elle est disponible ;
4. synchronise et indexe les sources ;
5. te fait renseigner une seule fois ton profil et ton UID ;
6. installe une tâche Windows quotidienne de mise à jour ;
7. vérifie le serveur MCP et les tests.

Ensuite, double-clique sur `START_IRMINSUL.bat`, ou lance :

```powershell
claude
```

Claude Code utilisera automatiquement l'agent `irminsul-orchestrator` configuré dans `.claude/settings.json`.


### Entretien

- `UPDATE_IRMINSUL.bat` force immédiatement la mise à jour des sources et de gcsim.
- La tâche Windows `IrminsulDailyUpdate` actualise automatiquement la base chaque nuit.
- `UNINSTALL_IRMINSUL.bat` retire proprement la tâche automatique sans supprimer tes données.
- En cas de doute sur l'état de l'installation : `irminsul doctor` (vérifie Python, gcsim, l'index local, les sources et la fraîcheur).

## Premières commandes utiles

```text
/genshin-import-good E:\...\genshinData_GOOD_2026_06_26_23_40.json   # importe ton compte réel
/genshin-account                 # résumé fiable du compte importé
/genshin-character Neuvillette    # analyse d'un perso possédé
/genshin-team Construis mes deux meilleures équipes pour l'Abîme actuel
/genshin-abyss                   # deux équipes simultanées sans objet partagé
/genshin-dps Compare les rotations de mes deux équipes avec mes vrais builds
/genshin-build Optimise mon build de Furina sans voler les artefacts de Neuvillette
/genshin-artifacts               # classe et optimise mon stock d'artéfacts
/genshin-weapons                 # meilleure répartition de mes armes
/genshin-farm                    # plan de farm selon mes matériaux
/genshin-upgrade                 # améliorations classées par rendement
/genshin-meta Fais un rapport de la meta actuelle en séparant ST, AoE et confort
/genshin-leaks Analyse ces leaks et classe leur fiabilité
```

Import et exploitation du compte (Inventory Kamera / GOOD) : voir **[docs/ACCOUNT_IMPORT.md](docs/ACCOUNT_IMPORT.md)**.
Le compte importé (`data/account/`) reste **local** et n'est jamais committé.

## Philosophie de calcul

- Pour un coup isolé : formule locale transparente via `calculate_direct_hit`.
- Pour une rotation ou une équipe : gcsim, avec hypothèses affichées.
- Pour une recommandation meta : croisement de données live, KQM, gcsim et contraintes réelles du compte.
- Les taux d'utilisation ou classements communautaires ne sont jamais traités seuls comme preuve de puissance.

## Sources synchronisées

- KQM Theorycrafting Library : mécanique et recherches vérifiées.
- gcsim : simulation Monte-Carlo d'équipes et rotations.
- genshin-db : données structurées de personnages, armes et objets.
- KQM GINews : archive d'actualités en jeu.
- Genshin Optimizer : référence de formats et optimisation d'artefacts.
- Enka.Network : import du showcase public d'un UID, avec cache respectant le TTL.

Les URLs, niveaux de confiance et règles d'usage sont dans `config/sources.yaml` et `docs/SOURCE_POLICY.md`.

## Limites honnêtes

Aucun système ne peut garantir automatiquement une meta parfaite juste après chaque patch : les rotations, bugs, mécaniques cachées et résultats de tests évoluent. Irminsul AI affiche donc toujours la date des données, les hypothèses et le niveau de confiance. Les leaks ne sont jamais fusionnés avec les données live et ne sont utilisés qu'en mode explicite.
