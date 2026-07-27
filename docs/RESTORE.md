# Remonter le projet après une réinitialisation du PC

Tout le **code** vit sur GitHub (`NylenIA/Irminsul`, branche `flutter-app`).
Ce qui n'y est pas, volontairement : les **données personnelles** (le dépôt
est public) et tout ce qui se régénère.

## 1. Récupérer le code

```bash
git clone https://github.com/NylenIA/Irminsul.git
cd Irminsul
git checkout flutter-app
gh auth setup-git   # sinon `git push` redemandera un mot de passe
```

## 2. Récupérer l'app compilée

Pas besoin de compiler : la release **`dev-latest`** contient
`Irminsul-windows.zip` (app + moteur gcsim). Elle est reconstruite
automatiquement chaque nuit à 06 h 30 UTC.

## 3. Restaurer tes données (depuis l'archive de sauvegarde)

L'archive `irminsul-sauvegarde-<date>.zip` contient ce que GitHub n'a pas :

| Dans l'archive | Où le remettre | Ce que c'est |
|---|---|---|
| `app/account.good.json` | `%APPDATA%\com.nylenia\irminsul\` | ta box importée |
| `app/account.meta.json` | idem | nom du fichier importé |
| `app/shared_preferences.json` | idem | **tes équipes créées** + cache des simulations |
| `app/mes-equipes-creees.json` | — | les mêmes équipes, lisibles sans l'app |
| `repo/data/account/` | racine du dépôt | analyses dérivées de ton compte |
| `repo/.mcp.json` | racine du dépôt | configuration des serveurs MCP |

Sans l'archive, rien n'est perdu côté app : il suffit de réimporter un export
GOOD (Inventory Kamera). Seules **les équipes créées à la main** et le cache de
simulations ne se reconstituent pas tout seuls.

## 4. Ce qui se régénère sans rien faire

- `data/sources/` (genshin-db, gcsim, KQM, datamine) — resynchronisé à la demande ;
- `data/irminsul.db` et `data/cache/` — reconstruits ;
- les icônes de personnages — retéléchargées au premier lancement ;
- `irminsul_app/windows/` — recréé par la CI (`flutter create`).

## 5. Outils à réinstaller sur la machine

Python 3.11+, Git, GitHub CLI (`gh`). **Flutter et Go ne sont pas nécessaires** :
la CI compile l'app et le moteur. Utile seulement si tu veux compiler en local.

## 6. Vérifier que tout va bien

```bash
python irminsul_app/tool/dart_sanity.py irminsul_app/lib
```

Puis, dans l'app : importer le GOOD, ouvrir **Équipes**, lancer une simulation.
Si un personnage récent s'affiche « pas encore simulable », c'est que la liste
`assets/data/gcsim_chars.json` du build est plus vieille que le moteur —
elle est régénérée à chaque build depuis le moteur réellement compilé.
