# MCP — configs prêtes à appliquer + procédures de test

> Décision : ne PAS modifier le `.mcp.json` partagé tant qu'un serveur n'a pas été **réellement testé**
> (prompt §6.2/§14). Les serveurs `npx` auto-démarrés s'exécutent à chaque session Claude Code du
> dépôt (y compris desktop/Python) — on ne les ajoute donc qu'une fois validés interactivement.
> `.mcp.json` actuel = `irminsul` seul (préservé).

## 1. next-devtools — PRÊT À APPLIQUER (faisable)
Package vérifié : `next-devtools-mcp@0.4.0` (stdio). Fusion non destructive à ajouter dans `.mcp.json` :
```json
"next-devtools": { "command": "npx", "args": ["-y", "next-devtools-mcp@0.4.0"] }
```
**Test (session interactive requise) :**
1. `npm run dev -w @irminsul/web` (Next dev server actif).
2. Dans Claude Code : approuver le serveur projet, puis `claude mcp list` / `claude mcp get next-devtools`.
3. Tester les outils réels : métadonnées projet, routes, erreurs, logs.
   → Le test n'est valide **que** si le dev server tourne et que le MCP interroge l'app réelle.
**Statut : READY (non testé ici, faute de session interactive + dev server).**

## 2. supabase — BLOCKED
- Docker **absent** + Supabase CLI **absent** → local impossible.
- Distant → auth OAuth interactive (`/mcp`) indisponible + **aucun projet Supabase** + **aucun besoin produit énoncé** (voir `docs/audit/RISKS_AND_BLOCKERS.md` R1/R2).
- Config (NE PAS appliquer tant que R1 non tranché et environnement non prêt) :
```json
"supabase": { "type": "http",
  "url": "https://mcp.supabase.com/mcp?project_ref=${SUPABASE_PROJECT_REF}&read_only=true&features=database,docs" }
```
**Statut : BLOCKED. Aucune donnée de compte ne doit aller vers un cloud.**

## 3. prisma-local — PENDING (dépend d'une base justifiée)
N'a de sens qu'avec un `prisma/schema.prisma` et un cas d'usage de base de données validé (R1).
```json
"prisma-local": { "command": "npx", "args": ["-y", "prisma", "mcp"] }
```
**Statut : PENDING (pas de schéma, base non justifiée). Ne pas ajouter à vide.**

## Tableau récap
| Serveur | Scope | Config prête | Auth | Statut test |
|---|---|---|---|---|
| irminsul | projet | en place | — | OK (existant) |
| next-devtools | projet | oui (0.4.0) | aucune | READY — non testé (session interactive requise) |
| supabase | projet | oui (gabarit) | OAuth interactif | BLOCKED (env + besoin) |
| prisma-local | projet | oui (gabarit) | aucune | PENDING (schéma/DB) |
