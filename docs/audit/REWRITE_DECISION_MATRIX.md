# Matrice de décision — KEEP / REFACTOR / MIGRATE / REWRITE / DELETE / BLOCKED

> Verdict par zone, avec preuve, risque, tests, dépendances. 2026-06-30.

| Zone | Verdict | Preuve | Risque | Tests / Dépendances |
|---|---|---|---|---|
| Moteur Python `src/irminsul/` | **KEEP** | 3124 LOC, 96 tests, goldens vs jeu, déterministe, sourcé, 0 TODO | Faible | 96 tests existants ; aucune raison de réécrire |
| Tauri desktop `app/src-tauri/` | **KEEP** | build MSI/NSIS produit, sidecar OK | Faible | `cargo test` (5) ; cargo hors PATH (R4) |
| Pont `engine.ts` + protocole sidecar | **KEEP / abstraire** | frontière nette, typée | Faible | À exposer via `packages/engine-client` pour la cible web |
| Frontend Vite/React (2 vues) | **MIGRATE** | surfaces minces, TS strict | Faible | Logique réutilisable → `packages/ui` (design system partagé) |
| Design system / tokens | **REWRITE** | CSS 99 lignes, pas de tokens centralisés | Faible | Cible : tokens OKLCH (mission redesign) — **bâti UNE fois dans `packages/ui`** pour desktop + web |
| App web | **CREATE** | n'existe pas | Moyen | Next.js 16.2.9 (stable vérifié) dans `apps/web`, additif |
| MCP `next-devtools` + `prisma-local` | **ADD (faisable)** | packages réels (0.4.0 / prisma 7.8) | Faible | À ajouter quand l'app/le schéma existent (sinon serveurs MCP en erreur) |
| **Supabase (Postgres cloud + Auth + RLS)** | **BLOCKED** | Docker+CLI absents ; auth OAuth interactive indispo ; **aucune fonctionnalité utilisateur ne l'exige** ; conflit privacy/offline (MASTER_SPEC §7) | **Élevé** (privacy, coût, complexité) | Ne pas construire tant qu'un besoin serveur concret n'est pas défini. Aucune donnée de compte vers le cloud. |
| **Prisma / `data-access`** | **BLOCKED-pending-DB** | n'a de sens qu'avec une base justifiée | Moyen | Scaffolding possible mais sans cas d'usage = code mort. Reporté jusqu'à R1 tranché. |
| MCP `irminsul` | **KEEP** | fonctionnel | Faible | Préserver intégralement dans `.mcp.json` |
| `duo-agents-fork` | **DELETE (hors scope)** | dépôt voisin distinct | — | Interdit par la mission ; ne pas toucher |

## Lecture
- **Cœur d'Irminsul = KEEP** (moteur + desktop + pont). Rien à réécrire côté logique métier.
- **Travail web légitime** = `apps/web` (Next.js) + `packages/ui` (design system unique) + `packages/engine-client` (interface stable vers le moteur). **Zéro base de données nécessaire** pour ça.
- **Supabase/Prisma = BLOCKED** faute de (1) besoin produit énoncé, (2) faisabilité environnementale, (3) compatibilité avec le caractère local/privé. Décision produit requise du propriétaire (voir R1).
