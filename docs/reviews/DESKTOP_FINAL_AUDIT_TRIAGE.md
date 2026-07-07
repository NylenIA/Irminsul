# Triage — audit Codex final (installation, Diagnostic, IO natif, nonce, cycle de vie)

> Reçu : `.duo/runtime/codex-audit-final2.md` (gpt-5.4-mini, worktree isolé — non détourné).

| # | Sévérité | Finding | Décision | Correction / Preuve |
|---|---|---|---|---|
| 1 | **Medium** | `account_import_good(path)` (bridge path-based hérité de l'UI Vite) exposé à la WebView via la capability loopback → une page loopback avec IPC pouvait importer un chemin GOOD arbitraire, contournant les dialogues natifs. | **accepted + fixed** | commande **retirée de l'invoke_handler** (fn conservé `#[allow(dead_code)]` avec note : l'import GOOD desktop futur passera par un dialogue natif). cargo 11/11 ; re-smoke installé |
| 2 | **Low** | `maskPath` ne couvrait que `Users/Utilisateurs` → un chemin absolu hors motif (temp/UNC) pouvait fuiter dans la page/copie. | **accepted + fixed** | redaction GÉNÉRALISÉE : tout chemin lecteur/UNC → `~…/<basename>` ; smoke vérifie l'absence du nom de compte (dérivé de l'env) |
| 3 | **Low** | Smoke : username en dur, pas de test cookie invalide, `/boot` valide non testé, smoke-errors absent du worktree d'audit. | **accepted + fixed (partiel documenté)** | username dérivé de `USERPROFILE` ; +test POST cookie **invalide** → 403 ; smoke-errors.mjs déjà commité (`ececfeb`, 4/4) — absence = timing du worktree ; `/boot` VALIDE intestable de l'extérieur **par conception** (nonce en mémoire seulement, documenté dans le script et le modèle de menace) |

## Vérifications positives (confirmées par l'audit)
`save_export_file`/`pick_import_file` sans chemin arbitraire ✅ · `default_name` assaini suffisant ✅ ·
pas de bypass méthode/matcher du middleware ✅ · nonce : aucune persistance/log, timing-safe non
requis (32 octets aléatoires, menace locale opportuniste) ✅ · cycle de vie propre, trou kill-forcé
assumé et documenté ✅ · bind-race résiduel = risque accepté documenté (DESKTOP_SECURITY_MODEL) ✅.
