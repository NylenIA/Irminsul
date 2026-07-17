# Avancement Irminsul — recalculé (reproductible)

> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json` le 2026-07-17. Branche `feat/irminsul-complete-redesign`. Ne pas éditer à la main.

## Scores
- **MVP utilisable : 83%**
- **Vision complète : 83%**
- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).
- Échelle : 0=absent, 25=squelette/mock/TODO, 50=happy-path peu validé, 75=intégré+testé cas majeurs, 100=prêt à livrer

## Détail par domaine
| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |
|---|--:|--:|--:|---|---|---|
| Moteur de données et calcul | 25 | 30 | 86 | high | Moteur stats finales INTEGRE (basestats+weaponstats+talentstats+charstats, defensif) ; pytest 232 ; goldens vs jeu ; registre mecaniques verified ; Lunar-Charged (1.8) + Lunar-Crystallize (1.6) LIVRES bout-en-bout via API lunaire generique (formules KQM sourcees, EM 6x/(x+2000), agregation 1/0.5/1/12/1/12, sidecar+miroir TS 6 goldens croises+UI apercu, E2E 48) | Lunar-Bloom (multiplicateur non confirme par KQM -> exclu volontairement, ajout trivial des confirmation) ; gcsim nouveaux persos |
| Intégration moteur | 15 | 12 | 85 | high | Stats finales LIVE (sidecar character_final_stats -> charstats, adapter final-stats/1.0, /characters/[id] avec breakdown/provenance/confiance) + apercu + reactions ; parite prouvee ; verrou phase3 leve | additives dans l'UI ; sidecar par defaut |
| Application web | 15 | 10 | 87 | high | Next.js 16.2.9 ; 9 surfaces (+ /diagnostic provenance moteur sanitizee) ; E2E 44/44 ; axe 0 critique ; resolution moteur unifiee (gele en desktop) | diagnostics UI ; desktop packaging |
| Application desktop | 10 | 12 | 82 | high | PROUVE bout-en-bout: install NSIS %LOCALAPPDATA%/Irminsul (exit 0, raccourci) + smoke INSTALLE tout vert (7 routes 200 dont /diagnostic, node lie au PID Tauri, port via table TCP, nonce POST/boot->403, zero orphelin x2, persistance) + desinstall (donnees conservees) + reinstall (DB non ecrasee) ; cas d'erreur 4/4 (sidecar/node/standalone absents->app vivante sans enfant ; double lancement) chemin Unicode+espaces. Diagnostic livre, IO natif Tauri, nonce ephemere. | MSI 1603 (per-machine sans elevation) ; non signe (SmartScreen) ; bind-race residuel accepte |
| Team builder et simulation | 15 | 15 | 87 | medium | Team Lab CRUD + reactions + rotations chiffrees + COMPARATEUR quantitatif (team-compare/1.0, 2 rotations meme cible, verdict si complet) + RECOMMANDATIONS deterministes (recommendations/1.0, donnees reelles, explicables) | gcsim ; energie/cooldown ; buffs par action |
| Persistance | 5 | 8 | 82 | high | Prisma 6 + SQLite ; TeamRepository CRUD + importTeams TRANSACTIONNEL (rollback) ; export/import versionne irminsul-export/1.0 avec checksum | chemins %APPDATA% pour desktop |
| Design system et UX | 5 | 5 | 65 | medium | tokens OKLCH + primitives + effets astral (halo, energie, skeleton, badges provenance/confiance) reduced-motion safe | Select/Tabs/Toast/CharacterPicker ; brand guide |
| Tests et qualite | 5 | 4 | 75 | high | 96 Python ; build ; 4 tests repository Vitest ; E2E Playwright 6 (save/reload/delete) ; axe a11y vert (0 critique/serieux) | couverture composants UI ; lint non cable |
| Packaging et deploiement | 3 | 2 | 74 | medium | NSIS installe/desinstalle/reinstalle PROUVE (per-user, sans admin) ; MSI produit mais 1603 sans elevation (preuve msi-install-1603.log) | MSI requiert admin ; non signe |
| Documentation et continuite | 2 | 2 | 75 | high | audit complet, DECISIONS, ARCHITECTURE, SESSION_HANDOFF, hook SessionStart | hook non encore enregistre dans settings |

_Recalcule : `python scripts/project_progress.py`._
