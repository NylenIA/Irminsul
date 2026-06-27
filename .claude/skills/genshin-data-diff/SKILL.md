---
name: Genshin Data Diff
description: Compare deux jeux de données (deux snapshots GOOD, deux versions de méta/kit) et résume les changements.
argument-hint: "<deux scans GOOD | deux versions à comparer>"
---
Compare les données : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §2, §5.
1. **Snapshots GOOD** : l'import (`irminsul.account.diff_snapshots`) détecte nouveaux persos, constellations, niveaux, talents, armes, raffinements, artéfacts ajoutés/retirés, équipements, variations de matériaux. Présente le diff.
2. **Méta/kit** : compare deux versions (dates, sources, ce qui a changé et pourquoi) ; sépare LIVE vs bêta/leak.
3. Signale toute incohérence ou donnée obsolète. Ne déduis rien d'absent → `safe_unknown`.
