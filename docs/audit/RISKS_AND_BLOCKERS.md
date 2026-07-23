# Risques et blocages (audit pré-Next.js)

> Classés par gravité. Un blocage = un fait vérifié qui empêche un critère d'acceptation.

## R1 — Architecture cloud non justifiée (gravité ÉLEVÉE) — décision produit
Supabase/Prisma = base Postgres cloud + Auth + RLS. Irminsul est **local, hors-ligne, mono-utilisateur, privé** (MASTER_SPEC §7 : les données du compte ne quittent jamais la machine). **Aucun des deux prompts n'énonce une fonctionnalité utilisateur** nécessitant une base serveur.
- **Risque** : régression privacy (données compte → cloud), perte du hors-ligne, coût récurrent, explosion de complexité pour un mainteneur solo.
- **Recommandation** : avant toute base de données, définir le **besoin concret** (ex. *sync multi-appareils de builds*, *profils publics partageables*, *classements*). Si pas de tel besoin → **pas de Supabase/Prisma**. Pour une version web, alternative locale-first : Next.js qui réutilise le moteur via une interface stable, données en local/IndexedDB, sans cloud.

## R2 — Blocages environnementaux Supabase (gravité ÉLEVÉE) — non franchissable par moi
- **Docker absent** + **Supabase CLI absent** → stack Supabase **locale impossible**.
- Distant → auth **OAuth interactive via `/mcp`** (indisponible en session non interactive) + **aucun projet Supabase** n'existe.
- **Conséquence** : le critère « Supabase MCP connecté en read-only » **ne peut pas être satisfait par moi**. Je ne le déclarerai jamais réussi sans sortie réelle.

## R3 — Pont moteur absent de la base de branche (gravité MOYENNE)
La branche redesign est sur `main`, sans `engine.ts`/`QuickCalc` enrichis de `feat/combat-engine-phase3` (PR #3, +459 lignes frontend). La vertical slice web « vraies données » exige soit la fusion de PR #3, soit un `packages/engine-client` exposant le moteur. → slice web initiale = **mock explicitement isolé** (autorisé prompt §5.4) jusqu'à résolution.

## R4 — `cargo` hors PATH (gravité FAIBLE)
`tauri:dev`/`tauri:build` échouent sans `export PATH="$HOME/.cargo/bin:$PATH"`. Correctif permanent : PATH utilisateur Windows.

## R5 — Complexité de stack (gravité MOYENNE)
Tauri + Python + Next.js + (Supabase + Prisma) + 4 MCP = surface de maintenance lourde pour un projet solo. Recommandation : design system + engine-client **mutualisés** (`packages/`) pour éviter le doublon desktop/web ; n'ajouter une couche que si une fonctionnalité la justifie.

## R6 — Deux missions partiellement contradictoires (gravité MOYENNE) — réconcilié
Mission « redesign Vite/Tauri » vs mission « web Next.js ». Réconciliation retenue : **architecture hybride**, design system bâti **une seule fois** dans `packages/ui`, consommé par desktop ET web. Le redesign n'est pas perdu : il devient le design system partagé.

## Outillage prescrit absent (rappel)
SkillSpector, `/impeccable`, `/plugin marketplace`, pnpm, Docker, Supabase CLI : absents → process adapté, sans simuler leur présence.
