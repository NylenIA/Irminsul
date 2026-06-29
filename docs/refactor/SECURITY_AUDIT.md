# SECURITY_AUDIT (2026-06-29) — lecture seule (priorité #1)

> Aucune modification appliquée (phase audit). Correctifs critiques **petits et isolés** uniquement
> pendant la PR #3 ; le reste → branche `refactor/pro-ui-security` + threat model + tests sécurité.

## Posture actuelle — points forts (mesurés)
- **Surface IPC minimale** : capabilities = `core:default` + `dialog:allow-open` **seulement**. Aucun plugin
  `shell`/`fs` ; seul `tauri-plugin-dialog`. 8 commandes maison (`account_*`, `quick_calc`, `mechanics`, `character_stats`) — pas d'exécution arbitraire.
- **CSP** : `default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'` — script restreint à 'self'.
- **Sidecar** : protocole borné (taille requête/réponse, timeout+kill, erreurs typées), **aucun secret en argument** (tout sur stdin),
  spawn direct (pas de shell), `CREATE_NO_WINDOW`. **`allow_nan=False`** (durci) → jamais de JSON non conforme.
- **Données joueur** : `data/account/`, `.claude/agent-memory/`, GOOD gitignorés. **Aucun secret** dans le dépôt.

## Constats / risques (sévérité)
| # | Constat | Sév. | Emplacement | Impact | Correction proposée | Statut |
|---|---------|------|-------------|--------|---------------------|--------|
| S1 | `style-src 'unsafe-inline'` dans la CSP | faible | tauri.conf.json | styles inline autorisés (XSS via CSS limité) | viser des styles non-inline (nonce/hash) à la refonte UI | deferred-with-reason |
| S2 | **Pas de lockfile Python** (ranges pip) | moyen | pyproject.toml | supply-chain non figée (CI non `--frozen`) | introduire `uv.lock`/`pip-tools` + install figé en CI (addendum §5.7) | deferred-with-reason |
| S3 | Import GOOD = lecture d'un chemin **choisi par l'utilisateur** (dialog) ; validation/atomicité à reconfirmer | moyen | account.py (import_good) | JSON non fiable, types, écriture | re-vérifier : validation stricte listes/objets, écriture temp→atomique, manifeste en dernier, verrou (addendum §5.2) | to-verify |
| S4 | Sortie d'erreurs sidecar → frontend : vérifier l'absence de chemins internes sensibles | faible | sidecar.py/lib.rs | fuite de chemins | expurger les messages d'erreur publics (redactor) | to-verify |
| S5 | Dépendances : pas d'audit automatisé (`npm audit`, `pip-audit`, `cargo audit`) en CI | moyen | CI | vulnérabilités non détectées | ajouter les 3 audits à la CI (non bloquant d'abord) | deferred |
| S6 | Pas de threat model formalisé | moyen | docs | angles morts | écrire `docs/refactor/THREAT_MODEL.md` (import GOOD, Enka, web search, sidecar, prompt-injection) | deferred |
| S7 | **Sécurité collaboration Duo/Codex** : incident `engine.ts` | — | externe | modif hors mission | **RÉSOLU/mitigé** : Codex read-only, test d'intégrité, scheduler désactivé (cf. INCIDENT_engine_ts.md) | accepted |

## Petits correctifs sécurité « critiques » autorisés pendant la PR #3
- Aucun **critique** ouvert détecté côté code livré (la surface est déjà minimale + sidecar durci).
- S2/S3/S5 sont **moyens** → à traiter en branche refonte (ou S2 tôt si la CI le permet sans risque PR #3).

## Prochaine étape sécurité
1. Vérifier S3 (atomicité/validation import GOOD) — **lecture du code** d'abord, correctif seulement si défaut réel.
2. Écrire le threat model (S6) + brancher `pip-audit`/`npm audit`/`cargo audit` en CI (S5, non bloquant).
