# Avancement Irminsul — recalculé (reproductible)

> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json` le 2026-06-30. Branche `feat/irminsul-complete-redesign`. Ne pas éditer à la main.

## Scores
- **MVP utilisable : 60%**
- **Vision complète : 58%**
- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).
- Échelle : 0=absent, 25=squelette/mock/TODO, 50=happy-path peu validé, 75=intégré+testé cas majeurs, 100=prêt à livrer

## Détail par domaine
| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |
|---|--:|--:|--:|---|---|---|
| Moteur de données et calcul | 25 | 30 | 75 | high | 20 modules Python / 96 tests / goldens vs jeu / registre mécaniques (basestats, talentstats, weaponstats verified) | réactions Lunaires + gcsim nouveaux persos manquants |
| Intégration moteur | 15 | 12 | 50 | medium | engine.ts<->sidecar Python OK (desktop, Phase 2-3) | packages/engine-client (web) absent |
| Application web | 15 | 10 | 50 | high | Next.js 16.2.9 ; route /team-lab (server-rendered) build+typecheck OK ; design system branche | E2E navigateur, autres ecrans |
| Application desktop | 10 | 12 | 50 | high | Tauri MSI/NSIS produit ; vues Compte + Calcul rapide branchees | Tableau de bord / Equipes / gcsim / Assistant vides |
| Team builder et simulation | 15 | 15 | 50 | medium | page Team Lab (Next.js) build OK, cablee TeamRepository (save/load/delete + validation Codex) | E2E Playwright/a11y ; roster reel via engine-client ; simulation DPS |
| Persistance | 5 | 8 | 75 | medium | Prisma 6 + SQLite local ; TeamRepository teste (Vitest) ; cable a l'UI (Server Actions, build OK) | presets/builds ; rename/duplicate |
| Design system et UX | 5 | 5 | 50 | medium | packages/ui : tokens OKLCH 'Archive astrale' + Button/Card/States ; DESIGN_SYSTEM.md | Input/Select/Dialog/Tabs/CharacterPicker ; brand guide |
| Tests et qualite | 5 | 4 | 50 | medium | 96 tests Python ; next build ; test repository Vitest | E2E Playwright + a11y axe absents |
| Packaging et deploiement | 3 | 2 | 50 | medium | desktop MSI/NSIS (Phase 2) | web non deploye |
| Documentation et continuite | 2 | 2 | 75 | high | audit complet, DECISIONS, ARCHITECTURE, SESSION_HANDOFF, hook SessionStart | hook non encore enregistre dans settings |

_Recalcule : `python scripts/project_progress.py`._
