# Revue Codex R3 — PR #3, stats de base d'arme (commit `b3250d1`)

- **Réviseur** : Codex (via `duo run`, session `2026-06-28T19-51-02Z-e7ee4014`), lecture seule (aucun fichier modifié).
- **Verdict initial** : `changes-required`. **Triage + correctifs** : Claude (reproduction indépendante).

## Points OK (validés indépendamment par Codex)
1. **Formules & valeurs** : Codex a **recalculé 10 armes** et les a **croisées avec le wiki en jeu**
   (Dull Blade, Silver Sword, Black Tassel, Prototype Archaic, Favonius Lance, Mappa Mare, Snow-Tombed
   Starsilver, Whiteblind, Skyward Harp, Mistsplitter). Toutes concordent. → références indépendantes (§5.6).
2. **Caps & couples impossibles** : OK (1-2★ → niv 70 / asc 4 ; couples incohérents rejetés).
3. **Unités secondaires** : OK (pourcentages ×100, EM brute ; `FIGHT_PROP_NONE` → secondaire null).

## Constats traités

| # | Constat | Sévérité | Triage | Correction | Test |
|---|---------|----------|--------|-----------|------|
| 4 | `compute_final_stats` fait trop confiance au payload arme : `{supported:true}` sans `base_atk` → 0 silencieux ; `base_atk=NaN`/`sec=Inf` → métadonnées NaN et `complete` peut rester vrai | **moyen** | **accepted** | `weapon_valid` exigé (ATQ de base finie + secondaire finie si clé) ; sinon arme exclue, `complete=false`, note explicite ; métadonnées via `_num` (jamais NaN). Champ `weapon.valid` exposé. | `test_invalid_weapon_payload_not_silently_complete` |
| 4b | Course async UI + `?? 0` masquant une valeur rejetée | moyen | **déjà corrigé** (R2/C5, commit `cfa13a6`) : jeton de requête + réinit. immédiate ; `?? 0` ne concerne que crit/EM (quasi jamais None) | — | typecheck |
| 5 | Registre non promouvable : extracteur déclare `reproducible` sans hash d'entrée ni contrôle de propreté ; formulation « complète » trop large ; URL KQM obsolète | moyen | **accepted (partiel)** | Garder `probable`. Formulation registre nuancée (= écran du jeu, pas stat de combat) ; sources élargies (wiki indépendant) ; golden élargi aux **10 cas** Codex. **À faire pour `verified`** : hash SHA256 des fichiers source + contrôle de propreté du checkout (documenté dans le registre). | `test_golden_independent_ingame` (10 cas) |

**Rejetés** : aucun. **Reportés** : durcissement extraction (hash/dirty-check) → condition de passage `verified` (documenté).

## Validation après correctifs
Ruff + **202 tests Python** (+11 : 10 golden armes indépendants + payload arme invalide), `tsc` strict +
`vite build`, sidecar autonome sans Python + app packagée (exe+MSI+NSIS).

**Statut registre** : `weapon_base_stats` reste **`probable`** (R3 OK sur formules/valeurs ; promotion `verified`
conditionnée au durcissement extraction). Aucune fusion avant CI verte + ce durcissement.
