# Guide d'exploitation

## Mise à jour

```powershell
uv run irminsul update
```

Cette commande synchronise les dépôts activés puis reconstruit l'index SQLite FTS.

## État

```powershell
uv run irminsul status
```

## Import Enka

```powershell
uv run irminsul account import-enka 700000000
```

Le showcase doit être public. Le cache respecte le champ `ttl` de l'API.

## Recherche locale

```powershell
uv run irminsul search "internal cooldown dendro"
```

## Calcul d'un coup

```powershell
uv run irminsul damage hit --scaling 2.5 --stat 2200 --crit-rate 0.75 --crit-damage 1.8
```

## Calcul d'une réaction

```powershell
uv run irminsul reaction transformative hyperbloom --em 200
uv run irminsul reaction amplifying forward-vaporize --em 120 --reaction-bonus 0.15
```

Les transformatives (Hyperbloom, Burgeon, Overload, Swirl, Superconduct…) ne crit pas.
Le multiplicateur amplifiant (Vaporize/Melt) s'injecte ensuite dans `damage hit
--reaction-multiplier`.

## Score d'un leak

```powershell
uv run irminsul leak score --provenance 4 --evidence 4 --corroboration 3 --track-record 4 --specificity 4 --stage late-beta
```

## Auto-diagnostic

```powershell
uv run irminsul doctor
```

Vérifie Python, le binaire gcsim, l'index local, la présence des sources et la
fraîcheur de la base. Code de sortie 1 si un élément manque.

## gcsim

Place un fichier `.txt` dans `simulations/`, puis :

```powershell
uv run irminsul gcsim run simulations\mon-equipe.txt
```
