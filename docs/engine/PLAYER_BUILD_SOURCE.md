# Builds réels du compte — source, adapter, limites

> Source : scan **InventoryKamera 1.4.3** au format **GOOD v3** importé le **2026-06-26**
> (`data/account/current/`, gitignoré — données personnelles ; SHA-256 conservé au profil).

## Chaîne
`DirectHitPreview (sélection perso)` → `loadPlayerBuildAction` (Server Action, lit le scan
**côté serveur**, seul le DTO du perso demandé part au client) → `normalizePlayerBuild`
(pur, testé, `packages/engine-client/src/player-build.ts`).

## Ce que le scan fournit (affiché avec provenance + confiance haute)
niveau, ascension, constellation, talents (auto/skill/burst), arme (id + raffinement,
parsée depuis la réf GOOD), emplacements d'artéfacts scannés.

## Ce qui MANQUE (affiché « jamais estimé »)
- **Stats finales** (ATQ/crit/EM réelles) : leur calcul (basestats + weaponstats + artéfacts
  résolus) vit dans le moteur **phase3 non fusionné** → la saisie du multiplicateur et de la
  stat porteuse reste **manuelle**. Aucune stat n'est inventée.
- Personnage absent du scan → état explicite « absent du scan » ; pas de scan → saisie manuelle.

## Confiance
`high` uniquement si le profil atteste `format: GOOD` d'un scanner connu ; sinon `medium`.
La date d'import est affichée — un scan vieux de plusieurs semaines peut différer du jeu.
