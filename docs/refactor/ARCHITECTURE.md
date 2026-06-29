# ARCHITECTURE_AUDIT (2026-06-29) — lecture seule

## Carte des modules
```
Frontend (Vite+React+TS strict)      Pont (Tauri 2 / Rust)        Moteur (Python, stdlib only au runtime sidecar)
  App.tsx → views/{Account,QuickCalc} ──IPC stdin/stdout JSON──►  sidecar.py → account_ipc.dispatch → {account, charstats,
  engine.ts (couche typée invoke)        lib.rs (8 commandes,        quickcalc, basestats, weaponstats, talentstats,
                                          spawn sidecar borné)        damage, reaction} + data/mechanics/*.json
```

## Points forts (à préserver)
- **Séparation nette** frontend / pont Rust / moteur Python ; IPC borné (id, timeout+kill, taille max, erreurs typées).
- **Moteur = stdlib only** au runtime → sidecar autonome (Python non requis). Données mécaniques **versionnées+sourcées**.
- **Dispatch unique** (`account_ipc.dispatch`) réutilisé par CLI et sidecar → une seule surface logique.
- `engine.ts` = couche typée unique vers les commandes Tauri (bon point de contrôle des contrats).

## Constats (sévérité)
| # | Constat | Sév. | Fichier | Impact | Correction (refonte) |
|---|---------|------|---------|--------|----------------------|
| A1 | `QuickCalc.tsx` 413 LOC : vue + état + logique d'affichage stats/armes/talents mêlés | moyen | app/src/views/QuickCalc.tsx | testabilité/maintenabilité | extraire hooks (`useCharacterStats`) + sous-composants (BaseStatsPanel, TalentPicker, ResultDetail) ; logique hors composant |
| A2 | Logique métier dans les composants (préremplissage, mapping talents) | moyen | QuickCalc.tsx | duplication, couplage | déplacer en modules purs testés (`app/src/domain/`) |
| A3 | `account.py` 721 LOC (import + validation + normalisation + overview) | moyen | src/irminsul/account.py | module fourre-tout | scinder : `good_io` / `validation` / `normalize` / `overview` |
| A4 | Pas de frontière de modules formalisée côté Python (imports croisés charstats↔basestats↔weaponstats↔talentstats) | faible | src/irminsul/ | couplage implicite | définir une couche `domain` (stats) vs `io` (account/sources) ; contrats explicites |
| A5 | Aucune dépendance circulaire détectée (imports linéaires) | — | — | — | RAS (à re-vérifier avec un linter d'imports) |
| A6 | Front : un seul fichier `engine.ts` mêle types + appels ; pas de séparation types/clients | faible | engine.ts | grossit avec les features | scinder `types.ts` / `client.ts` |

## Dépendances / couplage
- Pas de cycle d'import observé. `charstats` dépend de `basestats`+`weaponstats`+`talentstats` (sens descendant cohérent).
- **Frontière à introduire** : `domain` (calcul pur, sans I/O) vs `infra` (account/sources/sidecar) — facilite tests + perf.

## Recommandation
Refonte **incrémentale, sans réécriture** : (1) extraire la logique des gros composants/modules vers des unités
pures testées ; (2) formaliser une couche `domain` ; (3) ne PAS toucher les formules (PR #3) — uniquement la structure.
