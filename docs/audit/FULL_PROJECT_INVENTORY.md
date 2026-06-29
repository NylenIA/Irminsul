# Inventaire complet du projet Irminsul (audit pré-Next.js)

> 2026-06-30 · branche `feat/irminsul-complete-redesign` · faits issus de commandes exécutées.

## Stack réelle
| Couche | Techno | Preuve |
|---|---|---|
| Moteur | Python 3.14, **20 modules / 3124 LOC** | `src/irminsul/*.py` |
| Tests moteur | **16 fichiers / 96 tests** | `tests/*.py` |
| Desktop | Tauri 2.11 (Rust 1.96) | `app/src-tauri/` |
| Frontend | Vite 5.4 + React 18 + TS strict | `app/src/` (5 fichiers : App, engine, main, Account, QuickCalc) |
| Pont | Rust `lib.rs` ↔ sidecar Python (stdin/stdout) ; `engine.ts` typé | `app/src/engine.ts`, `app/src-tauri/src/lib.rs` |
| MCP (dev) | `irminsul` (lanceur Python, timeout 600s) | `.mcp.json` |
| Données | **locales** : GOOD, SQLite, `data/account/` (gitignoré) | CLAUDE.md, MASTER_SPEC §7 |

## Ce qui n'existe PAS (vérifié)
- **Aucune base de données relationnelle** (pas de Postgres, Prisma, ORM, migrations).
- **Aucun backend serveur / API HTTP** (le MCP est stdio ; le sidecar est stdin/stdout).
- **Aucune authentification / multi-utilisateur** (app mono-joueur).
- **Aucune dépendance cloud à l'exécution** (offline ; Claude API optionnelle non encore branchée).
- **0 TODO/FIXME** dans `src/` et `app/src/`.
- **pnpm absent** → gestionnaire réel = **npm** (`app/package-lock.json`) ; pas de `package.json` racine / workspace.

## Qualité de code observée
- Moteur : couvert (96 tests, goldens vs jeu), déterministe, sourcé (registre de mécaniques). **Faible dette.**
- Frontend : minimal mais propre (TS strict, a11y de base, zéro donnée factice). **Surface fonctionnelle limitée** (Compte + Calcul rapide ; Tableau de bord/Équipes/gcsim/Assistant = placeholders).

## Versions externes résolues (pour la cible web)
- Next.js stable `latest = 16.2.9` ✓ · `next-devtools-mcp` 0.4.0 ✓ · Prisma 7.8.0 ✓ · `@supabase/mcp-server-supabase` 0.8.2 ✓.
- Docker **absent** · Supabase CLI **absent** · `claude` CLI 2.1.195 présent.
