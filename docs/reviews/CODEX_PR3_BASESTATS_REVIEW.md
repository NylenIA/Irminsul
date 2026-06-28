# Revue Codex — PR #3, incrément « stats de base personnage »

- **Réviseur** : Codex (via `duo run`), lecture seule (sandbox read-only — aucun fichier modifié).
- **Session** : `2026-06-28T12-08-00-606Z-9f544814` · **Verdict initial** : `changes-required`.
- **Triage + correctifs** : Claude (lead). Chaque constat a été **reproduit indépendamment** avant correction.

> Note : le bac à sable lecture seule a empêché Codex d'écrire ce rapport ; il l'a transmis en
> résumé compact. Le détail ci-dessous est la **reproduction Claude** de chaque constat (cycle §3.3).

## Constats, triage et corrections

| # | Constat Codex | Sévérité | Triage | Reproduction (preuve) | Correction | Test de non-régression |
|---|---------------|----------|--------|------------------------|-----------|------------------------|
| C1 | Validation niveau/ascension insuffisante | moyen | **accepted** | `character_base_stats("HuTao",90,0)` renvoyait HP 10580 (paire impossible en jeu) au lieu d'une erreur | Bornes `ASCENSION_LEVEL_FLOOR/CAP` ; rejet explicite des paires impossibles | `test_impossible_level_ascension_pair_rejected` |
| C2 | `Traveler*` trop permissif | faible | **accepted** | `normalize_key("TravelerNonsense")` → `aether`, signalé *supported* | Seules les variantes connues (`anemo…cryo`, `Aether/Lumine/Traveler`) → `aether` ; inconnu = non pris en charge | `test_traveler_unknown_variant_not_silently_aether` |
| C3 | NaN/infini acceptés silencieusement | **élevé** | **accepted** | `compute_final_stats` produisait `atk=nan`, `crit_rate=inf` ; `calculate_direct_hit(nan,…)` passait (`nan<0` = False) | Garde `math.isfinite` : substats GOOD (skip+anomalie), sorties `final_stats` (jamais NaN/inf), `calculate_direct_hit` (rejet entrées non finies), `basestats` (sortie finie) | `test_substat_non_finite_flagged_not_summed`, `test_final_stats_never_emit_nan`, `test_rejects_non_finite_inputs`, `test_property_outputs_always_finite_nonnegative` |
| C4 | Incomplétudes d'artéfact perdues | moyen | **accepted** | `compute_final_stats` ignorait `uncomputed_main` → stat finale incomplète mais non signalée (seule l'arme l'était) | `final_stats` répercute chaque stat principale non calculée sur la cellule concernée + liste `artifact_main_incomplete` | `test_uncomputed_main_marks_final_stat_incomplete` |
| C5 | ATQ UI périmée | faible | **accepted** | Au changement de perso (vers non-supporté / désélection), `f.stat` gardait l'ATQ du perso précédent | `selectCharacter` vide/réinitialise `stat` ; garde `value:null` (jamais "NaN") | typecheck strict + build Vite (UI) |
| C6 | Provenance non reproductible | moyen | **accepted** | `extracted_at = date.today()` → diff non reproductible à chaque extraction | `extracted_at` dérivé du **commit source** ; flag `reproducible` ; confiance abaissée si pas de commit | `test_provenance_reproducible_flag` + vérif `diff` byte-identique sur 2 extractions |

**Constats rejetés** : aucun. **Reportés** : aucun (tous corrigés dans ce cycle).

## Validation après correctifs
- Ruff + **158 tests Python** (147 → 158, +11 non-régression) ✅
- TypeScript strict + build Vite ✅ · `cargo test` (5) ✅
- Sidecar autonome SANS Python (données embarquées) ✅ · App packagée (exe+MSI+NSIS) : import→perso→stats de base→calcul→relance ✅
- Données `character-basestats.json` régénérées et **reproductibles** (2 extractions identiques) ✅

## Contre-revue Codex R2 — FAITE (2026-06-28, après réinit quota)
Session `2026-06-28T19-40-06-350Z-f19fe51b`, lecture seule (aucun fichier modifié).
**Verdict : changes-required** — C1, C2, C4, C6 confirmés **OK** ; **résidus réels** sur C3 et C5
(reproduits par Claude, tous corrigés) :

| Résidu | Sévérité | Reproduction | Correction | Test |
|--------|----------|--------------|-----------|------|
| C3.1 base Crit non gardé (NaN renvoyé) | faible | `base_crit_rate_=NaN` renvoyé sans erreur | garde finie étendue à base CR/CD (`basestats.py`) | `test_base_crit_non_finite_rejected` |
| C3.2 anomalies stockent NaN brut → JSON invalide (JS) | moyen | `json.dumps(..., allow_nan=False)` échoue | valeur d'anomalie sérialisée en `str` + **`allow_nan=False` dans `sidecar._enc`** (filet final) | `test_anomalies_value_is_json_safe`, `test_enc_rejects_non_finite_no_invalid_json` |
| C3.3 métadonnées d'arme ré-émises sans garde | faible | `secondary_stat_value` non finie possible | `_finite_or_none` sur base_atk/secondaire (`charstats.py`) | couvert par `test_final_stats_never_emit_nan` |
| C3.4 `calculate_direct_hit` ignore `attacker_level`/`enemy_level` | moyen | `attacker_level=NaN` → résultat NaN | niveaux ajoutés à la garde finie (`damage.py`) | `test_rejects_non_finite_levels` |
| C5 course async ATQ (valeur périmée pendant l'await / réponse obsolète) | moyen | ATQ précédente réutilisable pendant la requête ; réponse ancienne écrase la courante | réinit. immédiate avant `await` + jeton de requête (`QuickCalc.tsx`) | typecheck + revue |

**Validation après résidus** : Ruff + **181 tests** ; `tsc` strict. Contre-revue finale (R2b) à confirmer.
