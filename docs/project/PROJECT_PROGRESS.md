# Avancement Irminsul — recalculé (reproductible)

> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json` le 2026-06-30. Branche `feat/irminsul-complete-redesign`. Ne pas éditer à la main.

## Scores
- **MVP utilisable : 64%**
- **Vision complète : 62%**
- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).
- Échelle : 0=absent, 25=squelette/mock/TODO, 50=happy-path peu validé, 75=intégré+testé cas majeurs, 100=prêt à livrer

## Détail par domaine
| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |
|---|--:|--:|--:|---|---|---|
| Moteur de données et calcul | 25 | 30 | 75 | high | 20 modules Python / 96 tests / goldens vs jeu / registre mécaniques (basestats, talentstats, weaponstats verified) | réactions Lunaires + gcsim nouveaux persos manquants |
| Intégration moteur | 15 | 12 | 50 | medium | engine.ts<->sidecar Python OK (desktop, Phase 2-3) | packages/engine-client (web) absent |
| Application web | 15 | 10 | 60 | high | Next.js 16.2.9 ; /team-lab build+typecheck OK + E2E Playwright vert (desktop+mobile) | autres ecrans (dashboard, compte web) |
| Application desktop | 10 | 12 | 50 | high | Tauri MSI/NSIS produit ; vues Compte + Calcul rapide branchees | Tableau de bord / Equipes / gcsim / Assistant vides |
| Team builder et simulation | 15 | 15 | 60 | medium | Team Lab : roster reel genshin-db (118) + save/reload/delete + regle anti-doublon + E2E vert | simulation DPS ; rename/duplicate UI ; roster synchronise au compte |
| Persistance | 5 | 8 | 75 | medium | Prisma 6 + SQLite local ; TeamRepository teste (Vitest) ; cable a l'UI (Server Actions, build OK) | presets/builds ; rename/duplicate |
| Design system et UX | 5 | 5 | 50 | medium | packages/ui : tokens OKLCH 'Archive astrale' + Button/Card/States ; DESIGN_SYSTEM.md | Input/Select/Dialog/Tabs/CharacterPicker ; brand guide |
| Tests et qualite | 5 | 4 | 75 | high | 96 Python ; build ; 4 tests repository Vitest ; E2E Playwright 6 (save/reload/delete) ; axe a11y vert (0 critique/serieux) | couverture composants UI ; lint non cable |
| Packaging et deploiement | 3 | 2 | 50 | medium | desktop MSI/NSIS (Phase 2) | web non deploye |
| Documentation et continuite | 2 | 2 | 75 | high | audit complet, DECISIONS, ARCHITECTURE, SESSION_HANDOFF, hook SessionStart | hook non encore enregistre dans settings |

_Recalcule : `python scripts/project_progress.py`._
