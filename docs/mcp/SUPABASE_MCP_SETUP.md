# Supabase MCP — préparé, non bloquant (local-first)

> Décision produit : Irminsul est **local-first**. Supabase = fonctions **futures et optionnelles**
> (sync volontaire, partage, communauté). **Aucune donnée privée n'est envoyée par défaut.**

## État officiel
```
SUPABASE_MCP = READY_FOR_USER_AUTH   (≠ CONNECTED)
```
Aucun projet Supabase ni OAuth disponible ici → on **prépare** sans connecter. Cela ne bloque rien d'autre.

## Ce qui est requis (non disponible dans cette session)
- Un **projet Supabase de développement** (jamais la production).
- L'**authentification OAuth** interactive (`claude mcp login supabase`).
- Docker + Supabase CLI seraient nécessaires **seulement** pour une stack *locale* (hors périmètre actuel).

## Procédure (quand un projet dev + OAuth seront disponibles)
1. `./scripts/configure-supabase-mcp.ps1 -ProjectRef <ref-dev>` (refuse une valeur vide ; read-only ; features=database,docs).
2. `claude mcp get supabase` puis `claude mcp login supabase`.
3. Tester en lecture seule : connexion, lecture du schéma, recherche de doc, infos projet dev, **absence d'écriture**.

## Sécurité
- Pas de PAT/secret en clair dans `.mcp.json` (OAuth uniquement).
- Read-only par défaut. Jamais la production. Suppression propre : `claude mcp remove supabase`.

## Adaptateur (préparé, pas activé)
L'UI dépend de l'interface `TeamRepository` (cf. `packages/data-access`). Implémentations :
- `PrismaSqliteTeamRepository` — **active maintenant** (local).
- `SupabaseTeamRepository` — **plus tard**, non codée tant qu'elle n'est pas testable.
