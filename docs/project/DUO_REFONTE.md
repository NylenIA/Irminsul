# Chantier A — Refonte Duo Control Center (audit + décision)

> Strictement séparé d'Irminsul. **Ne modifie jamais le moteur Irminsul.** Démarrage conditionné à une
> décision d'architecture (ci-dessous), car l'UI vit dans un **package npm externe**.

## Constat structurant (bloquant pour « démarrer la refonte »)
L'interface Duo est servie par le **package npm `duo-agents` v0.2.0** (MIT, 0 dépendance), installé global
sous `…/npm/node_modules/duo-agents/`. **Elle ne fait pas partie du dépôt Irminsul** et n'y est pas versionnée.
→ Modifier `node_modules/duo-agents` est **fragile** (écrasé à chaque `npm i -g`/update) et non traçable en revue.

### Décision requise (à toi)
- **Option F (recommandée)** : **forker** `duo-agents` (MIT) dans un dépôt/dossier dédié (ex. `tools/duo-agents-fork/`
  ou un repo séparé), refondre là-bas, puis lancer ce fork au lieu du package global. Traçable, réversible, versionné.
- **Option E** : éditer `node_modules` en place (rapide mais **non persistant/non versionné**) → déconseillé.
→ Tant que F n'est pas validée, je **n'édite pas** le package (cohérent avec « pas de modif hors mission » et l'incident).

## Cause racine du bug « messages invisibles/perdus » (caractérisée, lecture seule)
`src/dashboard.mjs` (UI vanilla JS, **pas React**) :
- **Polling** `setInterval(refresh, 1200)` sur `/api/snapshot` (pas de SSE/WebSocket) → events entre deux polls non garantis.
- `timeline.innerHTML = merged.slice(-200).map(...).join('')` → **(a)** plafond **200 events** (les plus anciens disparaissent),
  **(b)** **re-render complet** à chaque tick (perte de scroll, pas de clés stables, pas de dedup, scintillement),
  **(c)** dépend du « snapshot » côté `control-center.mjs` (`new Map()` de derniers messages) → un message non retenu = invisible.

### Correctifs ciblés (à faire APRÈS décision F, dans le fork)
1. **Source d'événements unique + IDs stables + dedup** (Map par `id`), ordre déterministe par timestamp+seq.
2. **Append incrémental** (pas de `innerHTML` global) + **scroll virtuel** pour gros historique + conservation de position.
3. **SSE/WebSocket** (ou polling delta `since=<seq>`) + reconnexion + replay + compteur de nouveaux messages.
4. Distinction visuelle humain/Claude/Codex/sous-agent/système/commande/test/décision ; persistance locale.
5. Monitoring honnête : modèle/auth/tokens/quota/reset/backoff **marqués `exact|estimated|unavailable`** (jamais inventés).
6. Tests : ordre, dedup, reconnexion, replay, gros historique, **aucune perte de message**, aucune popup.

## Scheduler Duo — sécurité & invisibilité (état)
- **DÉSACTIVÉ/désinstallé** (suite incident `engine.ts`). Wrapper `.duo/scheduler-resume.cmd` = `node duo.mjs scheduler tick`
  (aucun secret ; `containsSecrets:false` ; `policy: same-account-no-api-fallback`).
- **Invisibilité** : la tâche planifiée doit s'exécuter **fenêtre cachée** et **sans console visible** ; le wrapper `@echo off`
  va dans ce sens. À confirmer dans le fork : exécution hidden + logs redirigés (rotation), jamais de secret en clair.
- **Réactivation** : seulement quand (i) Codex read-only confirmé (✅ fait), (ii) les lancements programmés d'agents sont
  **bornés et sans auto-édition** des fichiers Irminsul (à garantir dans le fork), (iii) décision explicite (`duo scheduler enable`).

## Statut
- **Aucune modification du package Duo** appliquée (audit seul). Refonte Duo = **en attente de la décision F/E**.
- Anti-double-exécution + isolation Codex read-only + test d'intégrité = déjà en place côté Irminsul (cf. INCIDENT_engine_ts.md).
