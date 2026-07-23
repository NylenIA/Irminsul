# Audit de préparation de l'application desktop (Windows)

> Audité le 2026-07-04. **Aucune migration lancée** (politique : ne pas mettre en danger les
> tranches livrées). Ce document liste bloqueurs, dépendances, commandes, risques, prochaine tranche.

## État réel constaté
| Élément | Constat |
|---|---|
| Coque Tauri | `app/src-tauri/` — `productName: Irminsul`, `version: 0.1.0`, bundle **MSI + NSIS** actifs |
| Frontend embarqué | **Vite** (`frontendDist: ../dist`, `devUrl: localhost:5173`, `beforeDevCommand: npm run dev`) dans `app/src` |
| Sidecar | `externalBin: binaries/irminsul-sidecar` ; binaire présent `irminsul-sidecar-x86_64-pc-windows-msvc.exe` ; `app/src/engine.ts` l'invoque |
| Nouvelle UI produit | **Next.js** `apps/web` (Team Lab, /characters, /characters/[id], /rotations, /team-compare, /recommendations) — **PAS embarquée par Tauri** |
| Persistance | Prisma + SQLite (`DATABASE_URL`) côté `apps/web` (Server Actions) |
| Next.js output | mode **serveur par défaut** (Server Actions + Prisma) — pas d'`output: export` |

## Bloqueur principal (P0)
**Divergence de frontend** : la coque Tauri embarque l'ancienne UI Vite (`app/`), tandis que toute
la valeur récente (moteurs stats finales / rotations / comparateur / recommandations + leurs pages)
vit dans `apps/web` (Next.js). **Empaqueter la redesign en desktop nécessite une décision d'archi**,
car Next.js avec **Server Actions + Prisma** n'est pas exportable en statique (`output: export`) :
les actions serveur exigent un runtime.

### Options (à arbitrer, non tranchées ici)
1. **Next.js standalone embarqué** : bundler `next start` (mode standalone) comme process local lancé
   par Tauri (comme le sidecar), Tauri pointant sur `http://127.0.0.1:<port>`. + : réutilise tout le
   code. − : embarque Node + le serveur Next dans l'installeur (taille, démarrage).
2. **Sidecar-first (client pur)** : déplacer la logique Server Action vers des appels sidecar directs
   (le sidecar Python fait déjà les calculs) + persistance via un plugin Tauri SQL, et exporter
   l'UI en statique. + : installeur léger, pas de Node serveur. − : réécriture des Server Actions
   (teams CRUD, chargement compte) en commandes Tauri/sidecar.
3. **Rester sur l'app Vite** et y porter les pages : abandonne les Server Actions Next. − : duplication.

**Recommandation** : Option 1 pour une première release desktop rapide (réutilise 100 % du code
validé), puis évaluer l'Option 2 pour alléger. À décider avec l'utilisateur avant toute migration.

## Autres points (P1/P2)
- **Chemins Windows** : la résolution `process.cwd()/../..` des Server Actions (sidecar/scan) suppose
  la structure du monorepo → à remplacer par des chemins résolus à l'installation (dossier data
  utilisateur `%APPDATA%/Irminsul`) en desktop. (P1)
- **Données compte** : `data/account/current/` (gitignoré) doit devenir un dossier utilisateur
  writable, jamais dans les Program Files. (P1)
- **SQLite** : chemin DB à pointer vers `%APPDATA%/Irminsul` (writable) au lieu du repo. (P1)
- **Sidecar Python** : le binaire `irminsul-sidecar` doit exposer les méthodes actuelles
  (`character_final_stats`, `calculate_rotation`) — vérifier la parité avec `scripts/engine_stdio.py`
  avant packaging (le binaire date possiblement d'avant ces méthodes). (P0 pour la parité)
- **Popup console** : `windowsHide:true` déjà en place côté Node ; vérifier le spawn du sidecar Tauri. (P2)
- **Updater / icons / désinstallation** : non audités en profondeur (P2).

## Commandes de référence (non exécutées ici)
```
# build web standalone (option 1)
cd apps/web && npm run build   # nécessiterait next.config output:'standalone'
# build Tauri (coque actuelle, Vite)
cd app && npm run tauri build  # produit MSI/NSIS de l'ANCIENNE UI
```

## Prochaine tranche desktop (proposée)
1. Décider l'option d'archi (recommandé : 1).
2. Régénérer/valider le binaire sidecar avec parité `engine_stdio.py` (méthodes stats finales + rotation).
3. Externaliser les chemins (data/DB → `%APPDATA%/Irminsul`).
4. Embarquer Next standalone + pointer Tauri dessus ; smoke test lancement sans terminal, sans popup.
5. Installeur testable + désinstallation propre.

**Verdict** : desktop **non prêt** pour la redesign aujourd'hui (P0 = divergence frontend + parité
sidecar). La coque, le bundling MSI/NSIS et le mécanisme sidecar **existent** — la tranche est un
travail d'intégration cadré, pas une reconstruction.
