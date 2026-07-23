# Contrat de comparaison d'équipes — `team-compare/1.0`

> Comparateur QUANTITATIF : deux équipes, **deux rotations définies**, une **cible commune**.
> Réutilise `rotation/1.0` (aucune reconstruction). Guidance : `senior-architect`, `senior-qa`.

## Chaîne
```
UI (2 éditeurs de rotation + cible) → Server Action compareTeamsQuantitativeAction
  → sidecar calculate_rotation × 2 (MÊME enemy) → normalizeRotation × 2
  → compareTeamPerformance (PUR, TS) → verdict + écarts
```

## Règle d'honnêteté (cœur)
Un **verdict de DPS** n'est émis que si `left.complete && right.complete`. Sinon :
« Aucun verdict quantitatif fiable — au moins une rotation est incomplète ». Jamais de chiffre
inventé, jamais de score opaque unique. La cible est **identique** pour les deux (imposé par
le Server Action : une seule `EnemyTarget` passée aux deux rotations).

## Métriques comparées (`TeamMetricDifference`)
DPS moyen (plus haut = mieux), Dégâts totaux (plus haut = mieux), Durée (plus court = mieux).
Chaque écart : `absolute`, `relativePct`, `winner ∈ {left,right,tie,null}`, `computable`.
Une métrique dont un côté est `null` (rotation incomplète) → `computable:false` (jamais « comparée »).

## Bornes / sécurité
Cible bornée (niveau 1..200, résistance -1..3) côté Server Action + moteur. Validation de timeline
réutilisée (`validateRotation`) pour chaque côté avant appel moteur. Timeout sidecar 15 s. Aucun
chemin local renvoyé (provenance curée en amont).

## Confiance
`high` si les deux rotations complètes ; `low` sinon. La confiance reflète la complétude réelle,
jamais gonflée.

## Tests
`team-compare.test.ts` (5) : verdict quantitatif + écart relatif, une incomplète → pas de verdict,
égalité → tie, durée (plus court=mieux), hypothèses « même cible / pas un classement méta ».
