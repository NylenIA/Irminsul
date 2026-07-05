# ADR — Runtime desktop d'Irminsul

- **Statut** : accepté (Option A), spike runtime **prouvé exécutablement** ; build Tauri complet + packaging = tranche gated séparée.
- **Date** : 2026-07-04.

## État réel constaté (découverte, non supposé)
| Élément | Valeur vérifiée |
|---|---|
| Coque Tauri | `app/src-tauri`, `tauri = "2"`, bundle MSI+NSIS, `externalBin: binaries/irminsul-sidecar` |
| Frontend embarqué actuel | **Vite** (`frontendDist: ../dist`, `devUrl: localhost:5173`) — **ancien**, pas la redesign |
| Redesign | Next.js **16.2.9** (`apps/web`) : Server Actions + Prisma + sidecar Python |
| Mode de rendu | serveur par défaut (les routes utilisent `force-dynamic` + Server Actions) |
| Toolchain | cargo **1.96.0** présent (`~/.cargo/bin`, hors PATH) ; rustup absent ; **WiX/NSIS absents du PATH** |
| Build existant | `app/src-tauri/target/release/{irminsul.exe, irminsul-sidecar.exe}` (historique) |

## Exigences
Hors ligne, loopback only, réutiliser le code validé, Server Actions préservées, pas de serveur distant, installeur Windows.

## Options
### Option A — Next.js standalone embarqué (RETENUE)
Tauri lance `node .next/standalone/apps/web/server.js` (sidecar), WebView pointe sur `http://127.0.0.1:<port>`.

**Preuve de faisabilité minimale (exécutée, réelle) :**
```
# output:"standalone" ajouté à apps/web/next.config.ts
npm run build -w @irminsul/web  → émet apps/web/.next/standalone/apps/web/server.js
HOSTNAME=127.0.0.1 PORT=41777 node .next/standalone/apps/web/server.js
curl http://127.0.0.1:41777/    → HTTP 200, "Irminsul — Archive astrale"
```
→ **Le serveur standalone démarre, bind 127.0.0.1, sert les routes avec Server Actions.** ✅

- ✅ réutilise 100 % du code validé (7 routes, moteurs, Prisma).
- ✅ loopback, hors ligne (Prisma SQLite local + sidecar Python local).
- ⚠️ embarque un runtime Node dans l'installeur (taille/RAM/démarrage).
- ⚠️ Tauri doit gérer cycle de vie du process Node (spawn/kill) + health check.

### Option B — Frontend statique + commandes Tauri
Exporter l'UI en statique, déplacer les Server Actions vers des commandes Tauri/sidecar.
- ❌ **Non faisable sans réécriture** : Prisma + Server Actions (teams CRUD, chargement compte) ne
  s'exportent pas en statique. Volume de migration élevé, duplication de logique. **Rejetée pour V1.**

### Option C — rester sur l'app Vite
Abandonne la redesign. **Rejetée** (perte de toute la valeur récente).

## Matrice de décision (pondérée)
| Critère (poids) | A | B | C |
|---|---:|---:|---:|
| Réutilisation code (30) | 30 | 8 | 4 |
| Faisabilité prouvée (25) | 25 | 8 | 15 |
| Hors ligne/loopback (20) | 20 | 20 | 20 |
| Coût migration (15, ↑=moindre) | 12 | 3 | 6 |
| Surface d'attaque (10, ↑=moindre) | 6 | 9 | 8 |
| **Total /100** | **93** | **48** | **53** |

## Décision
**Option A**. Le spike prouve le runtime ; l'intégration Tauri consiste à (1) spawn du serveur Node
standalone en sidecar (port dynamique loopback), (2) health check borné avant d'afficher la WebView,
(3) kill du process à la fermeture.

## Risques / conséquences
- **P0 (build) — WiX/NSIS absents** : `tauri build` MSI/NSIS peut échouer au bundling (le binaire
  `.exe` reste productible). À installer avant packaging (`cargo tauri build` télécharge parfois NSIS).
- **P0 (parité sidecar)** : le binaire `irminsul-sidecar.exe` doit exposer `character_final_stats`
  + `calculate_rotation` (méthodes récentes). Voir mécanisme de provenance (Tranche C).
- **P1 (chemins)** : data/DB/scan → `%APPDATA%/Irminsul` (writable), pas le repo, en desktop.

## Stratégie de retour arrière
`output:"standalone"` est **inoffensif pour le web** (émet en plus le dossier standalone, ne change
pas le dev/build normal). Retrait = supprimer la ligne. Aucune régression web (E2E inchangés).

## Critères d'acceptation (gated, NON encore atteints)
- [ ] `cargo tauri build` produit un exécutable qui lance le serveur Node standalone.
- [ ] WebView affiche la redesign (pas Vite), routes critiques OK, aucun process orphelin à la fermeture.
- [ ] Smoke test sur le **binaire production** (pas `tauri dev`).
→ Tant que ces cases ne sont pas cochées avec preuve, **le desktop n'est PAS déclaré prêt**.
