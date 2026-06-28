# RISKS

| Risque | Impact | Mitigation |
|---|---|---|
| ~~Build Tauri local impossible (MSVC absent)~~ — **RÉSOLU 2026-06-28** | — | VS 2022 Build Tools (VCTools) installés ; `cargo check` OK ; **build release local produit** `irminsul.exe` + installeurs **MSI/NSIS**. CI `desktop.yml` reste la validation reproductible. |
| Règles par chemin non chargées pour une Q&A pure (sans toucher au code) | perte de contexte domaine | garder l'essentiel universel dans CLAUDE.md ; détail procédural dans skills invocables |
| 30 skills → catalogue large | coût si tout envoyé | chargement à la demande (descriptions courtes) ; recherche dynamique d'outils côté app (§10) |
| Données perso (UID/pseudo, GOOD) | exposition | `data/account/` gitignoré ; anonymisation déjà appliquée à l'historique poussé |
| Prompt caching app non finalisable sans gateway | gain partiel en Phase 0 | spécifié/préparé en Phase 0, finalisé en Phase 5 |
| Comptage de tokens = estimation locale (~chars/4) | imprécision | utiliser l'endpoint officiel de comptage avant opérations proches d'une limite (Phase 5) |
| Test handshake MCP stdio sensible à l'OS (0 outil sur ubuntu) | faux rouge CI | `skipif` Windows-only (régression `os.execv` propre à Windows) ; contrat outils couvert par un test unitaire toutes plateformes |
| Sidecar onefile : surcoût d'extraction par appel | latence légère | acceptable pour ops compte/calcul ponctuelles ; mode serveur long-vécu envisageable si besoin (mesurer avant d'optimiser) |
| Stats de base perso/arme absentes de la source locale (genshin-db raw sans courbes intégrées) | stats finales non auto | next session : extraire `data/.../curve` + valeurs de base, versionner+sourcer ; en attendant, ATQ/scaling saisis manuellement (étiquetés). Ne jamais approximer. |
| Dérive de version (coefficients/valeurs qui changent au patch) | données obsolètes | résoudre la version live au moment de la recherche ; ne pas graver « actuel » ; statut+date+source par mécanique dans le registre. |
