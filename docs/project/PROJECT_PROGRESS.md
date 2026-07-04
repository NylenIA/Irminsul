# Avancement Irminsul — recalculé (reproductible)

> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json` le 2026-06-30. Branche `feat/irminsul-complete-redesign`. Ne pas éditer à la main.

## Scores
- **MVP utilisable : 74%**
- **Vision complète : 74%**
- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).
- Échelle : 0=absent, 25=squelette/mock/TODO, 50=happy-path peu validé, 75=intégré+testé cas majeurs, 100=prêt à livrer

## Détail par domaine
| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |
|---|--:|--:|--:|---|---|---|
| Moteur de données et calcul | 25 | 30 | 82 | high | Moteur stats finales INTEGRE (basestats+weaponstats+talentstats+charstats, defensif) ; pytest 192 passed ; goldens vs jeu ; registre mecaniques verified | reactions Lunaires + gcsim nouveaux persos |
| Intégration moteur | 15 | 12 | 85 | high | Stats finales LIVE (sidecar character_final_stats -> charstats, adapter final-stats/1.0, /characters/[id] avec breakdown/provenance/confiance) + apercu + reactions ; parite prouvee ; verrou phase3 leve | additives dans l'UI ; sidecar par defaut |
| Application web | 15 | 10 | 72 | high | Next.js 16.2.9 ; 3 pages reelles (Dashboard honnete, /characters roster scanne avec provenance, /team-lab calcul+reactions) + nav accessible ; E2E 16/16 desktop+mobile, axe vert 3 pages | Comparateur/Rotations/Recommandations/Import-Export ecrans |
| Application desktop | 10 | 12 | 50 | high | Tauri MSI/NSIS produit ; vues Compte + Calcul rapide branchees | Tableau de bord / Equipes / gcsim / Assistant vides |
| Team builder et simulation | 15 | 15 | 78 | medium | Team Lab : CRUD + apercu avec 13 reactions selectionnables (amplifiantes integrees au coup, transformatives dediees) + panneau build reel du compte | rotations ; gcsim ; stats finales auto |
| Persistance | 5 | 8 | 75 | medium | Prisma 6 + SQLite local ; TeamRepository teste (Vitest) ; cable a l'UI (Server Actions, build OK) | presets/builds ; rename/duplicate |
| Design system et UX | 5 | 5 | 65 | medium | tokens OKLCH + primitives + effets astral (halo, energie, skeleton, badges provenance/confiance) reduced-motion safe | Select/Tabs/Toast/CharacterPicker ; brand guide |
| Tests et qualite | 5 | 4 | 75 | high | 96 Python ; build ; 4 tests repository Vitest ; E2E Playwright 6 (save/reload/delete) ; axe a11y vert (0 critique/serieux) | couverture composants UI ; lint non cable |
| Packaging et deploiement | 3 | 2 | 50 | medium | desktop MSI/NSIS (Phase 2) | web non deploye |
| Documentation et continuite | 2 | 2 | 75 | high | audit complet, DECISIONS, ARCHITECTURE, SESSION_HANDOFF, hook SessionStart | hook non encore enregistre dans settings |

_Recalcule : `python scripts/project_progress.py`._
