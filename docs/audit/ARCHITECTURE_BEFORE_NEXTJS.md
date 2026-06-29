# Architecture actuelle (avant introduction Next.js)

> Référence pour juger ce qui doit migrer, être conservé ou bloqué.

## Flux d'exécution réel
```
Utilisateur (fenêtre desktop)
  └─ React/Vite (app/src) ── engine.ts (typed) ──> invoke() Tauri
       └─ Rust (app/src-tauri/src/lib.rs) ── stdin/stdout (id, timeout, taille max) ──>
            └─ sidecar Python (PyInstaller, stdlib) ── src/irminsul/* (damage, reaction,
               account, team_optimizer, quickcalc, charstats, talentstats, weaponstats, gcsim…)
                 └─ données LOCALES (GOOD, registre mécaniques, data/account) — aucun réseau
```

## Propriétés clés (à préserver — MASTER_SPEC)
- **Local-first / hors-ligne** : tout le calcul et les données vivent sur la machine.
- **Privé** : le fichier GOOD / le compte ne quittent jamais la machine.
- **Mono-utilisateur** : pas d'auth, pas de session serveur.
- **Reproductible** : moteur déterministe, versionné, sourcé.
- **Distribuable sans Python** : sidecar embarqué (MSI/NSIS).

## Implication pour la cible web/cloud
Introduire Next.js (frontend web) est **additif et compatible** : un frontend web peut consommer le moteur via une interface stable (API locale ou réutilisation du sidecar).
Introduire **Supabase/Prisma (Postgres cloud + Auth + RLS)** n'a **aucun point d'ancrage** dans cette architecture : il n'existe ni donnée serveur, ni multi-utilisateur, ni besoin de persistance distante. Voir `REWRITE_DECISION_MATRIX.md` (verdict BLOCKED) et `RISKS_AND_BLOCKERS.md` (R1).
