# Architecture (cible hybride, local-first)

```
Irminsul/ (monorepo npm)
├─ app/                      # Desktop Tauri + React/Vite (EXISTANT, préservé)
├─ apps/
│  └─ web/                   # Next.js 16 App Router, TS strict (NOUVEAU)
├─ packages/
│  ├─ data-access/          # Prisma + SQLite local ; interface TeamRepository (NOUVEAU)
│  ├─ ui/                    # design system partagé « Archive astrale » (à construire)
│  └─ engine-client/        # interface typée stable vers le moteur (à construire)
├─ src/irminsul/             # Moteur Python (KEEP) — 20 modules, 96 tests, déterministe
├─ app/src-tauri/            # Rust : pont sidecar (KEEP)
└─ .mcp.json                # irminsul (stdio) + next-devtools (READY_FOR_APPROVAL)
```

## Règles de frontière
- **Local-first** : aucune donnée privée hors machine. Prisma = **serveur uniquement** (jamais dans un Client Component).
- L'UI dépend des **interfaces** (`TeamRepository`, `EngineClient`), pas des implémentations (Prisma/Supabase/sidecar).
- Le moteur Python reste accédé via une interface stable ; pas de réécriture pour le design.
- Web et desktop partagent `packages/ui` (design system) et, à terme, `packages/engine-client`.

## Flux persistance (local)
UI (`apps/web`, Server Action/route serveur) → `TeamRepository` → `PrismaSqliteTeamRepository` → SQLite (`dev.db`, gitignoré).

## Flux moteur (à finaliser)
UI → `EngineClient` → (desktop) commande Tauri→sidecar Python ; (web) à définir (API locale / réutilisation sidecar). Mock isolé tant que non branché.
