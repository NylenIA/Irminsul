# RISKS

| Risque | Impact | Mitigation |
|---|---|---|
| ~~Build Tauri local impossible (MSVC absent)~~ — **RÉSOLU 2026-06-28** | — | VS 2022 Build Tools (VCTools) installés ; `cargo check` OK ; **build release local produit** `irminsul.exe` + installeurs **MSI/NSIS**. CI `desktop.yml` reste la validation reproductible. |
| Règles par chemin non chargées pour une Q&A pure (sans toucher au code) | perte de contexte domaine | garder l'essentiel universel dans CLAUDE.md ; détail procédural dans skills invocables |
| 30 skills → catalogue large | coût si tout envoyé | chargement à la demande (descriptions courtes) ; recherche dynamique d'outils côté app (§10) |
| Données perso (UID/pseudo, GOOD) | exposition | `data/account/` gitignoré ; anonymisation déjà appliquée à l'historique poussé |
| Prompt caching app non finalisable sans gateway | gain partiel en Phase 0 | spécifié/préparé en Phase 0, finalisé en Phase 5 |
| Comptage de tokens = estimation locale (~chars/4) | imprécision | utiliser l'endpoint officiel de comptage avant opérations proches d'une limite (Phase 5) |
