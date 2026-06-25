# Démarrage rapide — Irminsul AI

Guide ultra-simple pour utiliser ton assistant Genshin dans Claude Code (Windows).
Tout est déjà installé : tu n'as rien à compiler ni à configurer pour commencer.

---

## 1. Ouvrir le projet et démarrer Irminsul

1. Ouvre le dossier du projet :
   `C:\Users\akuon\IA Genshin\Irminsul-AI-Claude-Code`
2. Double-clique sur **`START_IRMINSUL.bat`** (ou, dans un terminal placé dans ce
   dossier, tape `claude`).
3. À la première ouverture, Claude Code peut demander d'autoriser le **serveur MCP
   « irminsul »** : accepte une fois. L'agent **`irminsul-orchestrator`** se charge
   automatiquement.

Pour vérifier que tout va bien à tout moment :

```bat
.venv\Scripts\python.exe -m irminsul.cli doctor
```

Tu dois voir 5 lignes « OK » (Python, gcsim, index, sources, fraîcheur).

---

## 2. Renseigner ton UID (reste privé)

Deux possibilités :

- **Rapide, sans rien éditer** : dans Claude Code, tape
  `/genshin-account 700000000` (remplace par ton UID, 8 à 10 chiffres).
- **Mémorisé dans ton profil** : ouvre `profiles\player.yaml` et complète
  `uid:` et `server:`. (Si le fichier manque, copie `profiles\player.example.yaml`
  en `player.yaml`.)

> 🔒 `player.yaml` est exclu de Git : ton UID et tes préférences ne seront jamais
> publiés ni commités.

---

## 3. Importer un fichier GOOD (Genshin Optimizer)

1. Dans Genshin Optimizer : **Database → Export → Download to file** (format GOOD).
2. Dans Claude Code :
   `/genshin-import-good C:\chemin\vers\ton-export.json`

Le fichier d'origine n'est **jamais modifié**. Pour un test en ligne de commande :

```bat
.venv\Scripts\python.exe -m irminsul.cli account inspect-good "C:\chemin\export.json"
```

---

## 4. Analyser ton compte / demander une équipe / calculer un DPS

Dans Claude Code (exemples) :

| Objectif | Commande |
|---|---|
| Analyse de compte | `/genshin-account 700000000` |
| Deux meilleures équipes Abîme | `/genshin-team Construis mes 2 meilleures équipes pour l'Abîme actuel` |
| Comparer des DPS/rotations | `/genshin-dps Compare mes deux équipes avec mes vrais builds` |
| Optimiser un build | `/genshin-build Optimise Furina sans voler les artefacts de Neuvillette` |
| Rapport meta | `/genshin-meta Sépare ST, AoE et confort` |
| Rotation détaillée | `/genshin-rotation Donne la rotation optimale de Raiden National` |
| Plan de tirages | `/genshin-pulls Dois-je pull la prochaine bannière ?` |
| Lore (anti-spoiler) | `/genshin-lore Explique Khaenri'ah sans spoiler les quêtes récentes` |
| Analyse de leaks (séparée) | `/genshin-leaks Analyse et classe la fiabilité de ces leaks` |
| Vérifier une réponse | `/genshin-verify Vérifie toutes les affirmations ci-dessus` |

Calcul d'un coup isolé en CLI (exemple) :

```bat
.venv\Scripts\python.exe -m irminsul.cli damage hit --scaling 2.5 --stat 2000 --damage-bonus 0.466 --crit-rate 0.6 --crit-damage 1.4
```

Simulation gcsim (exemple reproductible fourni) :

```bat
.venv\Scripts\python.exe -m irminsul.cli gcsim run simulations\smoke-test.txt
```

---

## 5. Mettre les données à jour

- **Manuel, immédiat** : double-clique sur **`UPDATE_IRMINSUL.bat`**
  (resynchronise KQM, gcsim, genshin-db, GINews + retélécharge gcsim au besoin,
  puis réindexe).
- **Automatique (optionnel)** : la mise à jour quotidienne n'est **pas** activée par
  défaut. Pour l'activer, lance une fois dans PowerShell :
  ```powershell
  .\scripts\bootstrap.ps1 -SkipGcsim -SkipSources -SkipProfile
  ```
  (crée la tâche Windows `IrminsulDailyUpdate`, 03:17 chaque nuit).

---

## 6. Désinstaller la tâche automatique

Double-clique sur **`UNINSTALL_IRMINSUL.bat`**. Cela retire la tâche
`IrminsulDailyUpdate` **sans toucher** à tes données ni au projet.
(Si la tâche n'a jamais été activée, le script te le dira simplement.)

---

## 7. Résoudre les erreurs fréquentes

| Symptôme | Cause probable | Solution |
|---|---|---|
| `doctor` dit **gcsim À corriger** | binaire absent ou téléchargement coupé | `UPDATE_IRMINSUL.bat`, ou `.venv\Scripts\python.exe tools\install_gcsim.py` |
| **Index 0 documents** | base pas encore construite | `.venv\Scripts\python.exe -m irminsul.cli update --index-only` |
| Claude Code **ne voit pas l'outil MCP** | serveur non autorisé | relance `claude`, accepte le serveur « irminsul » ; vérifie que `.venv` existe |
| **Enka : profil indisponible (424)** | vitrine désactivée/vide en jeu | active l'affichage des personnages dans le jeu, réessaie après le TTL |
| **Enka : rate-limit (429)** | trop de requêtes | attends, le cache local est réutilisé automatiquement |
| **GOOD : « n'est pas un export GOOD valide »** | mauvais fichier exporté | réexporte au format **GOOD** depuis Genshin Optimizer |
| Accents bizarres dans la console | console en codepage hérité | déjà géré (sortie forcée en UTF-8) ; sinon `chcp 65001` |
| gcsim simulation impossible | config invalide pour la version | l'agent explique ce qui manque ; corrige la config ou relance `UPDATE` |

---

## Bon à savoir

- **OFFICIEL / LIVE / THÉORYCRAFT / SIMULATION / LEAK / SPÉCULATION** sont toujours
  séparés. Les **leaks** ne sont jamais mélangés aux données live et apparaissent
  sous une bannière `⚠️ LEAK NON CONFIRMÉ`.
- Chaque réponse importante affiche ses **hypothèses**, sa **date de données** et son
  **niveau de confiance**.
- Les chemins avec espaces (« IA Genshin ») fonctionnent : garde les guillemets dans
  tes commandes.
