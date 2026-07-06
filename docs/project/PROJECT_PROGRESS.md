# Avancement Irminsul — recalculé (reproductible)

> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json` le 2026-06-30. Branche `feat/irminsul-complete-redesign`. Ne pas éditer à la main.

## Scores
- **MVP utilisable : 81%**
- **Vision complète : 81%**
- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).
- Échelle : 0=absent, 25=squelette/mock/TODO, 50=happy-path peu validé, 75=intégré+testé cas majeurs, 100=prêt à livrer

## Détail par domaine
| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |
|---|--:|--:|--:|---|---|---|
| Moteur de données et calcul | 25 | 30 | 82 | high | Moteur stats finales INTEGRE (basestats+weaponstats+talentstats+charstats, defensif) ; pytest 192 passed ; goldens vs jeu ; registre mecaniques verified | reactions Lunaires + gcsim nouveaux persos |
| Intégration moteur | 15 | 12 | 85 | high | Stats finales LIVE (sidecar character_final_stats -> charstats, adapter final-stats/1.0, /characters/[id] avec breakdown/provenance/confiance) + apercu + reactions ; parite prouvee ; verrou phase3 leve | additives dans l'UI ; sidecar par defaut |
| Application web | 15 | 10 | 85 | high | Next.js 16.2.9 ; 8 surfaces reelles (+ /import-export versionne, aller-retour transactionnel teste) ; E2E 40/40, axe vert | diagnostics UI ; desktop packaging |
| Application desktop | 10 | 12 | 72 | high | PROUVE: build Tauri production PASS (exe+MSI+NSIS hashes), smoke binaire production TOUT VERT (6/6 routes 200, Next moderne, provenance sidecar frozen, zero orphelin x2, persistance DB), sidecar canonique rebuilt (parite testee sur .exe), Node embarque, donnees %APPDATA% | installation MSI/NSIS non testee de bout en bout ; signature absente (SmartScreen) ; M3 course port differe |
| Team builder et simulation | 15 | 15 | 87 | medium | Team Lab CRUD + reactions + rotations chiffrees + COMPARATEUR quantitatif (team-compare/1.0, 2 rotations meme cible, verdict si complet) + RECOMMANDATIONS deterministes (recommendations/1.0, donnees reelles, explicables) | gcsim ; energie/cooldown ; buffs par action |
| Persistance | 5 | 8 | 82 | high | Prisma 6 + SQLite ; TeamRepository CRUD + importTeams TRANSACTIONNEL (rollback) ; export/import versionne irminsul-export/1.0 avec checksum | chemins %APPDATA% pour desktop |
| Design system et UX | 5 | 5 | 65 | medium | tokens OKLCH + primitives + effets astral (halo, energie, skeleton, badges provenance/confiance) reduced-motion safe | Select/Tabs/Toast/CharacterPicker ; brand guide |
| Tests et qualite | 5 | 4 | 75 | high | 96 Python ; build ; 4 tests repository Vitest ; E2E Playwright 6 (save/reload/delete) ; axe a11y vert (0 critique/serieux) | couverture composants UI ; lint non cable |
| Packaging et deploiement | 3 | 2 | 70 | medium | MSI 100Mo + NSIS 63Mo produits et hashes (artifacts.txt) ; WiX/NSIS auto-provisionnes | install/desinstall non testees ; non signe |
| Documentation et continuite | 2 | 2 | 75 | high | audit complet, DECISIONS, ARCHITECTURE, SESSION_HANDOFF, hook SessionStart | hook non encore enregistre dans settings |

_Recalcule : `python scripts/project_progress.py`._
