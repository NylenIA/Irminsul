# Import et gestion du compte (Inventory Kamera / GOOD)

Ce guide explique comment alimenter Irminsul AI avec ton compte réel et l'exploiter
(équipes, builds, DPS, farm). **Tes données restent locales** : le brut et le
normalisé sont dans `.gitignore` (`data/account/`) et ne sont jamais envoyés à un
service externe sans ton accord.

## 1. Effectuer un nouveau scan Inventory Kamera
1. Lance **Inventory Kamera** (ce projet a été testé avec la v1.4.3).
2. Scanne au minimum : personnages, armes, artéfacts, matériaux.
3. Exporte au **format GOOD** (`version 3`). Tu obtiens un fichier du type
   `genshinData_GOOD_AAAA_MM_JJ_HH_MM.json`.

> Astuce : le Voyageur (Traveler) n'est souvent pas correctement scanné — il sera
> marqué « non résolu » (voir §5), c'est normal.

## 2. Où déposer le fichier
Tu peux pointer l'import **directement** sur le fichier exporté (n'importe quel chemin,
y compris un autre disque). L'import en fait une **copie en lecture seule** dans :

```
data/account/raw/<nom-du-fichier>.json
```

Le fichier d'origine n'est **jamais** modifié.

## 3. Lancer l'import
```bash
# depuis la racine du projet
PYTHONPATH=src .venv/Scripts/python.exe -m irminsul.cli \
  account import-good "CHEMIN/VERS/genshinData_GOOD_....json" --snapshot-date 2026-06-26
```
ou, côté agent : **`/genshin-import-good <chemin>`**.

L'import :
- valide le fichier (format, types, plages) ;
- calcule son **SHA-256** ;
- copie le brut en lecture seule dans `raw/` ;
- crée un **snapshot daté** `data/account/snapshots/<date>__<sha8>/` ;
- (ré)écrit la vérité courante dans `data/account/current/*.json` ;
- génère le rapport `data/account/reports/import-validation-<date>.md`.

**Idempotent** : réimporter le même fichier (même SHA-256) ne crée pas de doublon.
Utilise `--force` pour reconstruire un snapshot.

Structure produite :
```
data/account/
├── raw/             # copie brute en lecture seule
├── snapshots/       # un dossier daté par import
├── current/         # dernière vérité normalisée (7 fichiers JSON)
├── reports/         # rapports de validation
├── recommendations/ # analyses (ex. initial-account-analysis.md)
└── manifest.json    # journal des imports (SHA-256)
```

Chaque objet normalisé garde une `_provenance {array, index}` pointant vers le brut,
et un **identifiant interne stable** (le champ `id` d'Inventory Kamera n'est pas fiable :
plusieurs armes 1★ partagent `id=0`).

## 4. Lire le rapport de validation
Ouvre `data/account/reports/import-validation-<date>.md`. Les anomalies sont classées :
- **BLOCKING** : import impossible (ex. fichier non-GOOD) ;
- **ERROR** : donnée invalide (niveau/ascension/talent hors plage…) ;
- **WARNING** : anomalie récupérable (Traveler non résolu, ids dupliqués…) ;
- **INFO** : remarque.

## 5. Corriger une anomalie
- **Traveler / personnage non résolu** : conservé dans
  `data/account/current/unresolved-data.json`. Ses équipements sont listés, mais son
  élément/niveau/talents/constellation sont inconnus → **re-scan** ou saisie manuelle
  avant toute reco le concernant. Il est **exclu** des équipes principales.
- **`id` d'arme dupliqué** : aucune action requise, des ids internes stables sont utilisés.
- **ERROR de plage** : re-scanne le perso/objet concerné (souvent un scan partiel).

## 6. Comparer deux scans
Au prochain import, le pipeline compare automatiquement avec le **snapshot précédent**
et renvoie un diff : nouveaux personnages, constellations gagnées, niveaux/talents
améliorés, nouvelles armes, raffinements, artéfacts ajoutés/retirés, changements
d'équipement et variations de matériaux. Le diff figure dans le résultat de l'import.

## 7. Demander une équipe
- `/genshin-team <objectif>` — meilleures équipes avec tes persos possédés.
- `/genshin-abyss` — **deux** équipes simultanées sans partager perso/arme/artéfact.
- `/genshin-character <perso>` — analyse d'un perso et ses équipes possibles.

Les équipes n'utilisent que des objets **scannés** et respectent l'allocation exclusive.

## 8. Demander un calcul DPS
- `/genshin-dps <équipe ou perso>` — privilégie **gcsim** quand le perso/équipe est
  supporté, sinon un calcul déterministe documenté (formules, buffs, RES, DEF, réaction,
  niveau ennemi, durée de rotation, fourchette). Jamais une estimation présentée comme
  une simulation exacte.

## 9. Mettre à jour les données LIVE
- `/genshin-update` ou `irminsul update` — synchronise les sources et reconstruit l'index.
- `irminsul status` / `irminsul doctor` — fraîcheur et auto-diagnostic.
Vérifie toujours le **patch** et la **date** avant une reco méta.

## 10. Gérer les leaks
- `/genshin-leaks` — analyse **séparée** : provenance, date, score de fiabilité
  (`score_leak`), bannière « LEAK NON CONFIRMÉ ». Jamais mélangé silencieusement aux
  données LIVE ni intégré à une reco live sans demande explicite de planification future.

## 11. Sauvegarder le projet
- Le **code** est versionné par git ; `data/account/` est **ignoré** (données perso).
- Pour archiver ton compte : conserve tes exports GOOD (et/ou copie `data/account/`)
  hors dépôt. Chaque import est tracé dans `manifest.json` par SHA-256.

## 12. Validation globale
```bash
bash scripts/validate.sh        # ou : powershell -File scripts/validate.ps1
```
Lance Ruff + pytest (+ doctor informatif).
