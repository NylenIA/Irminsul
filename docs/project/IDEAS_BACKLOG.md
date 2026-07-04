# Backlog Irminsul — vagues essentielles restantes (non implémentées ce tour)

> Priorité au cœur produit. Ces éléments viennent des vagues du prompt FOCUS_CORE non encore
> traitées. Ordre = valeur produit / dépendances. Aucun n'est commencé tant qu'il n'est pas
> pris explicitement (évite le travail à moitié fait).

## Bloquant fondamental partagé
- **Stats finales du personnage** (ATQ/PV/DÉF/crit/EM effectifs) : calcul basestats + weaponstats
  + artéfacts résolus. Vit dans le moteur **phase3 non fusionné**. **Débloque** : rotations
  chiffrées, comparateur quantitatif, recommandations, préremplissage réel de l'aperçu.
  Tant qu'il n'est pas porté/fusionné, ces vagues restent qualitatives ou en saisie manuelle.

## Vagues restantes (essentielles)
1. **Rotations** (Vague 4) — modèle `RotationAction[]` + `RotationResult` (durée, DPS *seulement si*
   données complètes, sinon `rotation incomplète`/`données insuffisantes`). Dépend des stats finales
   pour un DPS ; le squelette temporel (timeline, field time, énergie) est faisable avant.
2. **Synergies** (Vague 5) — `SynergyInsight` explicable (éléments, réactions, batterie, driver,
   sustain), score seulement avec méthode documentée. Faisable qualitativement dès maintenant.
3. **Comparateur d'équipes** (Vague 6) — `/team-compare` : diffs directs/réactions/confort/survie
   + causes + compromis. Quantitatif après stats finales.
4. **Recommandations** (Vague 7) — moteur transparent (équipes/armes/artefacts à améliorer) avec
   justification + confiance + données manquantes. Jamais de classement opaque.
5. **Import/Export** (Vague 10) — export/import team+build JSON versionné + backup/restore SQLite +
   migration de version. Ne jamais écraser silencieusement.
6. **Desktop installable** (Vague 9) — vérifier/finaliser Tauri MSI/NSIS, sidecar propre, sans popup,
   crash recovery, désinstallation propre. Artefact testable.
7. **Primitives UI restantes** (§7) — Select, Tabs, Tooltip, Toast, DataTable, Chart, StatBlock,
   ProvenanceBadge, ConfidenceIndicator, ErrorBoundary — API stable + documentée.

## Nice-to-have (reporté explicitement par l'utilisateur)
- Pipeline d'analyse vidéo / « Claude Watch » — **gelé** (voir `docs/tools/CLAUDE_WATCH_AUDIT.md`).
