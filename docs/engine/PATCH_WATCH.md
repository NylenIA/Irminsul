# Veille patch — rester à jour sans casser les calculs

> Objectif (exigence Nylen) : à **chaque patch Genshin**, revalider systématiquement
> ce qui peut changer les chiffres, de façon **traçable**. Une veille n'est pas un
> événement ponctuel : c'est ce process, rejoué à chaque version.
> Complète [FORMULA_SOURCES.md](FORMULA_SOURCES.md) (le *quoi* est sourcé) par le *quand/comment* revalider.

## Pourquoi c'est critique
Le patch **5.2** a buffé 4 coefficients de réaction (EC/Overload/Superconduct/Shatter) — un bug
DPS réel qui a dormi jusqu'à l'audit. Sans veille, le moteur dérive silencieusement du jeu.

## Sources de référence (indexées localement)
| Source | Rôle | Rang |
|---|---|---|
| `kqm-tcl` (library.keqingmains.com) | formules, coefficients, mécaniques | A (primaire theorycraft) |
| `kqm-ginews` | annonces/patch notes KQM | A/B |
| `genshin-db` | données live (persos, armes, artéfacts, talents) | B |
| `gcsim` | vérité-terrain DPS (validé en jeu) | A (implémentation) |

## Outillage
```bash
irminsul status          # fraîcheur de l'index + des sources (repository_status)
irminsul update          # sync des repos sources + rebuild de l'index (refresh_knowledge)
bash scripts/validate.sh # ruff + pytest (garde anti-régression des constantes)
```
Sous-agent `live-data-researcher` : récupère les patch notes officiels + changements live.
Si l'index a > 24 h ou qu'un patch vient de sortir → `irminsul update` **avant** toute conclusion.

## Checklist à chaque nouveau patch
1. **Patch notes** : lire les notes officielles (via `live-data-researcher`) — chercher « reaction »,
   « multiplier », « Elemental Mastery », « Lunar », nouveaux persos/armes/sets.
2. **Sync** : `irminsul update` (kqm-tcl, kqm-ginews, genshin-db, gcsim) puis vérifier `irminsul status`.
3. **Revalider les constantes** de [FORMULA_SOURCES.md](FORMULA_SOURCES.md) SI le patch touche les réactions :
   - coefficients transformatifs (historique : 5.2) — croiser KQM TCL + gcsim ;
   - formules EM (transfo/ampli/additif/lunaire) ;
   - mains d'artéfacts 5★ niv20 (stables, mais surveiller un rework) ;
   - **Lunar-Bloom** : dès qu'un multiplicateur KQM fiable existe → l'ajouter (pipeline prêt).
4. **Nouveaux contenus** :
   - nouveaux persos/armes/sets → vérifier que `genshin-db` les fournit ; sinon marquer TODO ;
   - nouvelle réaction → l'ajouter **seulement** avec source rang A ; sinon avertissement, pas d'invention.
5. **Prouver** : si une constante change → maj Python + miroir TS + goldens régénérés + sidecar
   reconstruit + garde anti-régression + `verify` vert + entrée datée dans FORMULA_SOURCES.md.
6. **Tracer** : commit `chore(patch-watch): revalidation patch X.Y` même si rien ne change
   (« vérifié, RAS le AAAA-MM-JJ » est une information utile).

## Règles d'or (rappel dps.md)
- Jamais de valeur inventée : une mécanique incertaine = **avertissement**, pas fausse précision.
- Croiser ≥ 2 sources pour tout changement de constante DPS (leçon du 5.2).
- Séparer OFFICIEL / LIVE / THÉORYCRAFT / SIMULATION / LEAK.

## Journal de veille
| Date | Patch | Vérifié | Résultat |
|---|---|---|---|
| 2026-07 | ref. post-5.x | coefficients transfo, EM, mains artéfacts, lunaires | fix 5.2 appliqué ; reste conforme KQM |
