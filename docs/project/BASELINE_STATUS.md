# Baseline technique — préflight redesign (2026-06-30)

> Faits établis par commandes exécutées. Aucune valeur estimée.

## Stack détectée
- **Backend/moteur** : Python 3.14.3 (`src/irminsul/`, 23 modules) + sidecar PyInstaller (stdlib) embarqué.
- **Desktop** : Tauri 2.11 (Rust 1.96.0) ; frontend Vite 5.4 + React 18 + TypeScript strict.
- **Pont** : commandes Tauri (Rust `lib.rs`) → sidecar Python ; couche typée `app/src/engine.ts`.
- **gcsim** : v2.43.3 (`tools/bin/`).

## Commandes (lancer / tester / builder)
| But | Commande |
|---|---|
| Lint+tests Python | `bash scripts/validate.sh` (Ruff + pytest) |
| Tests Python ciblés | `.venv/Scripts/python -m pytest tests/ -q` |
| App en dev (desktop) | `npm --prefix app run tauri:dev` *(requiert `~/.cargo/bin` dans le PATH)* |
| Front seul (navigateur) | `npm --prefix app run dev` → http://localhost:5173 |
| Typecheck/build front | `npm --prefix app run build` (tsc --noEmit + vite build) |
| Build desktop | `npm --prefix app run tauri:build` (MSI + NSIS) |

## État vérifié au lancement de la mission
- **App lançable** : `tauri:dev` compile (Rust 1m19s) et ouvre la fenêtre (`irminsul.exe` observé en cours d'exécution, puis fermeture propre exit 0). Statut provisoire : **RUNNABLE_DEV_ONLY** (à reconfirmer par build packagé).
- **Tests** : 6/6 sur `test_leaks.py`+`test_mcp_server.py` (échantillon vérifié ce jour). Suite complète (≈226 selon STATUS phase3) **non encore relancée sur cette branche** → à mesurer.
- **2 écrans frontend fonctionnels** sur `main` : Compte, Calcul rapide (basique). Tableau de bord, Équipes, gcsim, Assistant = placeholders vides.

## Environnement — pièges connus (corrigés/à corriger)
- **`cargo` pas dans le PATH** du shell par défaut → `export PATH="$HOME/.cargo/bin:$PATH"` requis avant `tauri:dev`. (Correctif permanent recommandé : ajouter au PATH utilisateur Windows.)
- **Node v24.18.0 / npm 11.16.0 présents** (toolchain front opérationnel).
- **Vite EBUSY** (watcher surveillait `src-tauri/target/`) → corrigé dans `app/vite.config.ts` (exclusion `**/src-tauri/**`).

## Outillage prescrit par la mission mais ABSENT ici (impact)
- **SkillSpector** (audit sécurité des skills) : absent → classification HIGH/CRITICAL impossible → skills tiers non officiels **non auto-installés**.
- **Impeccable + `/impeccable …`, `/plugin marketplace`** : indisponibles (commandes de plugin interactives) → le process Phase A–E « piloté par Impeccable » est **adapté** : direction design via `frontend-design` + `web-design-guidelines` + revue/critique manuelle documentée.
