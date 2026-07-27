# Ajouter un personnage au moteur gcsim — méthode communautaire, reproduite

> Analyse menée le 2026-07-25 sur la PR Varka #2668 (Charlie-Zheng, mainteneur
> core — l'implémentation la plus récente) + le pipeline officiel (v2.44.0,
> « Add 6.7 Pipeline »). C'est le mode d'emploi pour implémenter nous-mêmes
> les persos manquants (Sandrone, Zibai, Nefer…).

## Anatomie d'un personnage (méthode Varka, ~1 750 lignes)

| Fichier | Rôle | Écrit par |
|---|---|---|
| `config.yml` | **Pilote de génération** : mappe les noms de talents du datamine vers des variables Go (`attack(1-Hit DMG)` → `attack[][]`) | main, ~50 lignes |
| `zz_<char>.dm.go` | **GÉNÉRÉ** : multiplicateurs par niveau de talent, enregistrement `core.RegisterCharFunc`, validation des params | pipeline (auto) |
| `<char>.go` | Classe : constantes (hits, énergie), `NewChar`, `Init` | main |
| `attack/skill/burst/charge.go` | Logique par action : **frames** (`N1→N2 = 23`), hitmarks, hitboxes, ICD, particules | main |
| `asc.go` / `cons.go` | Passifs A1/A4 et constellations C1-C6 | main |

Le catalog central (`pkg/catalog/character.dm.go` : stats de base, courbes,
élément, coût d'ulti) est aussi régénéré par le pipeline.

## Le pipeline officiel (la découverte qui change tout)

```
go run ./pipeline -s github:iam-akuzihs/excel/live
```
- Source de données : **datamine PUBLIC** (excel live + AnimeGameData en repli)
- La v2.44.0 a ajouté le « 6.7 Pipeline » → **les données de Sandrone & co
  sont déjà accessibles** à la génération
- Il suffit d'un `config.yml` par perso pour obtenir son `zz_*.dm.go` exact

## Ce qu'on peut reproduire, et à quel niveau de confiance

| Ingrédient | Source | Confiance |
|---|---|---|
| Multiplicateurs, stats, courbes, coût d'ulti | pipeline officiel (datamine public) | ✅ exact |
| Mécaniques du kit (états, buffs, ICD) | textes exacts du kit + doc gcsim | ✅ bon (à valider par sim) |
| **Frames** (durées d'animation) | KQM (86 persos mesurés — PAS les 6.x récents) | ⚠️ approximation depuis un perso de même arme, étiquetée |
| Réactions Lunaires (Sandrone…) | déjà implémentées dans le moteur (v2.43-2.44) | ✅ moteur prêt |

## Marche à suivre par perso (sous-étape 4.3.4b+)

1. `config.yml` calqué sur un perso similaire (Varka pour claymore)
2. Génération pipeline en CI (Go déjà installé) → `zz_*.dm.go` + catalog
3. Kit Go à la main, frames approximées du perso de même arme le plus proche
   (étiquette « frames approximées » dans l'app, marge ±10-15 %)
4. Compilation CI (replis en cascade déjà en place) + validation par
   simulation sur le GOOD réel + comparaison in-game (mode entraînement)
5. Garde-fou upstream : si gcsim merge le perso officiellement, notre version
   s'efface (pattern déjà appliqué à Iansan)

## Ordre de production proposé

1. **Sandrone** (possédée par l'utilisateur, DPS 6.7, interactions
   Stellar-Conduct — la plus utile mais la plus complexe)
2. Zibai, Nefer (selon la méta 6.7+)
3. Les autres au fil des besoins (Ifa, Illuga, Lohen, Linnea, Prune, Jahoda,
   Kachina, Manekin·a)

## Extraction des données SANS Go (2026-07-27)

La machine n'a pas Go : impossible de lancer `go run ./pipeline` en local.
`irminsul_app/tool/datamine.py` fait le même travail côté données, en Python,
en tapant directement les tables du jeu du dépôt public utilisé par le
pipeline (`iam-akuzihs/excel`, branche `live`, cache dans
`data/sources/datamine/`, gitignoré) :

```bash
python tool/datamine.py Sandrone            # résumé lisible
python tool/datamine.py Sandrone --json out.json
```

Chaîne : `genshin-db` (local) donne l'**avatarId** → `AvatarExcelConfigData`
donne stats de base, courbes et `skillDepotId` → `AvatarSkillDepotExcelConfigData`
donne les 3 talents → `AvatarSkillExcelConfigData` donne CD et coût d'ulti →
`ProudSkillExcelConfigData` donne les **multiplicateurs par niveau (1→15)**.
Les libellés de `genshin-db` (`combat1/2/3.attributes.labels`) disent ce que
chaque paramètre signifie, donc rien n'est deviné.

### Exemple vérifié : Sandrone (id 10000133)

5★ · claymore · Cryo · base HP 1029,6 / ATQ 26,6 / DÉF 58,6

| Talent | Valeurs (niveau 10) |
|---|---|
| Normale | 3 coups 150,8 % · 132,8 % · 203,2 % |
| Chargée | balayage 85 % · rayon condensé 242,3 % (+ Stellar-Conduct 161,5 %) |
| Plongeon | 147,4 % · bas/haut 294,8 % / 368,3 % |
| Compétence | tir prismatique 58,3 % (+ Stellar-Conduct 38,9 %) · CD 4 s |
| Ultime | bombardement 158,8 % ×3 · rayon 595,4 % (+ Stellar-Conduct 397 %) · CD 15 s · 60 énergie |

À noter : son kit tourne autour du **Stellar-Conduct**, précisément la
réaction que la 1ʳᵉ moitié de l'Abîme 6.7 amplifie (+75 %).

### Ce qui reste approximé (à étiqueter dans l'app)

Multiplicateurs, CD, coût d'énergie, stats : **exacts**. En revanche les
**frames d'animation**, les **particules générées** et le détail des passifs
et constellations ne sont pas dans ces tables : ils sont approchés à partir de
persos comparables (même arme, même rôle) et doivent être signalés comme tels
tant qu'un test in-game ne les confirme pas.

## État vérifié le 2026-07-25

- Iansan : ✅ portée par nous (PR #2374 modernisée), buff validé A/B (+24 %
  sur Mavuika), toujours absente de la source officielle
- Varka : ✅ PR #2668 fusionnée telle quelle dans notre build
- KQM frames locaux : 86 persos, aucun 6.x récent
- Ancien projet Python : aucun perso gcsim à récupérer (seul un smoke-test)
