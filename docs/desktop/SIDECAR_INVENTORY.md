# Inventaire & parité du sidecar moteur

> Vérifié le 2026-07-04 par exécution réelle (méthodes listées, SHA-256 calculé).

## Deux points d'entrée — DIVERGENCE réelle (bloqueur P0 desktop)
| | `scripts/engine_stdio.py` (web) | binaire empaqueté `irminsul-sidecar` |
|---|---|---|
| Source | `scripts/engine_stdio.py` | `src/irminsul/sidecar.py` → `account_ipc.dispatch` (PyInstaller) |
| Utilisé par | Server Actions Next (`SidecarEngineClient`) | coque Tauri (`externalBin`) |
| Méthodes | `calculate_direct_hit`, `amplifying_multiplier`, `transformative_reaction`, `character_final_stats`, `calculate_rotation`, `engine_provenance` | `profile`, `overview`, `roster`, `import-good`, `mechanics`, `quick-calc`, `characters`, `character-stats` |
| Rotations / réactions / apercu direct | ✅ | ❌ **absents** |

**Conséquence** : l'app desktop, si elle utilise le binaire empaqueté actuel, **ne peut pas** calculer
rotations, réactions ni aperçu de coup direct. Les deux entrées ont des jeux de méthodes **disjoints**.

## Inventaire du binaire empaqueté
| Champ | Valeur |
|---|---|
| Nom | `irminsul-sidecar-x86_64-pc-windows-msvc.exe` |
| Chemin dev | `app/src-tauri/binaries/` + `app/src-tauri/target/release/irminsul-sidecar.exe` |
| Chemin paquet | `externalBin: binaries/irminsul-sidecar` (résolu par triple) |
| Triple cible | `x86_64-pc-windows-msvc` |
| SHA-256 (préfixe) | `af0e0506aabd0f44…` |
| Source | `src/irminsul/sidecar.py` (PyInstaller, spec `.irminsul/pyi/…spec`) |
| Méthode de MAJ | régénérer via PyInstaller depuis la source unifiée |
| Cycle de vie | lancé/arrêté par Tauri (`externalBin`) |

## Mécanisme de provenance (livré, testable)
Nouvelle méthode `engine_provenance` de `engine_stdio.py` → l'app peut lire : `api_version`
(`engine-stdio/1.0`), `methods`, `contracts` (direct-hit/reactions/final-stats/rotation),
`git_commit`, `frozen_binary`, `python`. **But** : vérifier la parité réelle plutôt que supposer
qu'un `.exe` au nom plausible = le moteur testé.

## Résolution requise avant desktop (tranche future, non faite ici)
1. **Unifier l'entrée** : `src/irminsul/sidecar.py` doit exposer le sur-ensemble des méthodes
   (déléguer aussi à `engine_stdio` : rotation/réactions/final_stats), OU faire de `engine_stdio.py`
   la cible PyInstaller unique.
2. **Régénérer le binaire** depuis l'entrée unifiée + recalculer le SHA-256.
3. **Garde de parité** : l'app appelle `engine_provenance` au démarrage et refuse/alerte si
   `methods` ne couvre pas les contrats attendus (au lieu de crasher plus tard).

## Garde actuelle (test)
`tests/test_engine_stdio_parity.py` vérifie que `engine_stdio.py` expose bien le jeu de méthodes
attendu par le web (drift détecté si une méthode disparaît). La régénération du binaire empaqueté
reste un prérequis desktop **non satisfait**.
