# Triage Codex — TeamRepository

Date : 2026-06-30  
Source : `.duo/runtime/codex-review-team-repository.json`  
Portée : `packages/data-access/src/repositories/team-repository.ts` et `packages/data-access/tests/team-repository.test.ts`  
Statut : revue Codex terminée en lecture seule, sans `blocked by policy`.

## Verdict court

Le rapport Codex est globalement valide. Les deux sujets à traiter en priorité sont :

1. validation runtime de `SaveTeamInput` avant écriture Prisma ;
2. contrat d’erreur clair pour `getById(id)` / `delete(id)`.

Le sujet “séparation serveur/client” est réel architecturalement, mais moins urgent tant que le repository n’est pas encore importé par `apps/web`.

## Correctifs appliqués

Statut : appliqué le 2026-06-30.

- `save(input)` valide et normalise maintenant les données avant Prisma.
- `getById(id)` et `delete(id)` refusent les ids vides/blancs.
- `delete(id)` est maintenant idempotent pour un id valide inexistant.
- Le test repository n’utilise plus `npx prisma migrate deploy` pendant Vitest ; il applique les migrations SQL locales sur une base SQLite temporaire.
- La suite `@irminsul/data-access` passe : 4 tests, 4 réussis.

## À corriger maintenant

### 1. Validation runtime de `save(input)`

Sévérité : high  
Fichier : `packages/data-access/src/repositories/team-repository.ts`

Constat :

- `name` est persisté sans trim ni validation.
- `members` peut être vide ou contenir trop d’éléments.
- `slot` peut être dupliqué, hors plage ou non entier.
- `character` peut être vide.
- `role`, `carry`, `notes` ne sont pas normalisés.

Décision recommandée :

- Ajouter une fonction dédiée de validation/normalisation avant `db.savedTeam.create`.
- Règles minimales proposées :
  - `name.trim().length > 0`
  - `members.length` entre 1 et 4, ou exactement 4 si le Team Lab impose une équipe complète
  - `slot` entier unique entre `0` et `3`
  - `character.trim().length > 0`
  - `carry`, `role`, `notes` trim + `null` si chaîne vide

Tests à ajouter :

- nom vide ;
- membres vides ;
- plus de 4 membres ;
- slot dupliqué ;
- slot hors borne ;
- personnage vide ;
- normalisation des chaînes.

### 2. Contrat de `delete(id)` et validation des ids

Sévérité : medium  
Fichier : `packages/data-access/src/repositories/team-repository.ts`

Constat :

- `getById("")` et `delete("")` partent directement vers Prisma.
- `delete(id)` remonte une erreur Prisma brute si l’équipe n’existe pas.

Décision recommandée :

- Valider au minimum `id.trim().length > 0`.
- Choisir un contrat simple pour la suppression.

Choix recommandé pour l’instant :

- rendre `delete(id)` idempotent avec `deleteMany({ where: { id } })`.

Pourquoi :

- plus simple côté UI ;
- pas besoin de gérer une erreur technique pour une double suppression ;
- cohérent avec un bouton supprimer côté interface.

Tests à ajouter :

- `getById("")` ;
- `delete("")` ;
- suppression d’un id inexistant.

## À planifier après le wiring UI

### 3. Séparer les types partagés de l’implémentation Prisma

Sévérité : medium  
Fichier actuel : `packages/data-access/src/repositories/team-repository.ts`

Constat :

- les types `TeamRepository`, `SaveTeamInput`, `SavedTeamDTO` et l’implémentation `PrismaSqliteTeamRepository` sont dans le même module ;
- `packages/data-access/src/index.ts` ré-exporte actuellement tout depuis ce même module.

Risque :

- un import client Next.js peut accidentellement tirer un module serveur.

Triage :

- risque réel, mais pas bloquant immédiatement ;
- aucun import depuis `apps/web` n’a été trouvé au moment du triage.

Décision recommandée :

- avant de brancher `apps/web`, séparer :
  - `team-repository.types.ts` pour les contrats client-safe ;
  - `prisma-sqlite-team-repository.ts` pour l’implémentation serveur.

## À garder en observation

### 4. Mapping des erreurs Prisma

Sévérité : low/medium

Constat :

- les erreurs Prisma remontent telles quelles.

Triage :

- important à moyen terme pour remplacer Prisma/Supabase proprement ;
- pour l’instant, traiter seulement les erreurs directement liées à validation et suppression.

### 5. Transactions

Sévérité : low

Constat :

- `save()` utilise une nested write Prisma avec `members.create`.

Triage :

- pas de bug transactionnel évident pour la création actuelle ;
- une transaction explicite deviendra utile si `save()` évolue vers update/upsert, suppression/recréation de membres, ou plusieurs écritures séparées.

## Ordre d’exécution recommandé pour Claude

1. Ajouter les tests de validation et d’erreur.
2. Ajouter validation/normalisation dans le repository.
3. Rendre `delete(id)` idempotent ou documenter explicitement l’erreur domaine.
4. Relancer les tests `packages/data-access`.
5. Séparer les types/implémentation avant le branchement réel dans `apps/web`.

## Commandes utiles

```powershell
cd "C:\Users\akuon\IA Genshin\Irminsul-AI-Claude-Code"
Get-Content ".duo\runtime\codex-review-team-repository.json" -Raw
npm.cmd --workspace @irminsul/data-access test
```
