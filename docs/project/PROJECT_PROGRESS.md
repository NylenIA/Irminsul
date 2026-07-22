# Avancement Irminsul — recalculé (reproductible)

> Généré par `scripts/project_progress.py` depuis `PROJECT_PROGRESS.json` le 2026-07-17. Branche `feat/irminsul-complete-redesign`. Ne pas éditer à la main.

## Scores
- **MVP utilisable : 88%**
- **Vision complète : 88%**
- Confiance globale : moyenne (cœur moteur élevé ; surfaces web/UI récentes).
- Échelle : 0=absent, 25=squelette/mock/TODO, 50=happy-path peu validé, 75=intégré+testé cas majeurs, 100=prêt à livrer

## Détail par domaine
| Domaine | Poids | PoidsMVP | Score | Confiance | Preuve | Blocages |
|---|--:|--:|--:|---|---|---|
| Moteur de données et calcul | 25 | 30 | 90 | high | Moteur stats finales INTEGRE ; pytest 238 ; goldens vs jeu ; AUDIT SOURCE des formules (docs/engine/FORMULA_SOURCES.md, chaque constante sourcee KQM+corroboree) qui a corrige un VRAI bug DPS : coefficients transformatifs pre-5.2 -> post-5.2 (EC 2.0/OL 2.75/SC 1.5/Shatter 3.0, 3 sources concordantes, garde anti-regression) ; lunaires LC/LCrys + additives ; parite TS<->Python goldens croises | Lunar-Bloom (non confirme KQM -> exclu) ; veille patch pour revalidation continue des constantes |
| Intégration moteur | 15 | 12 | 91 | high | Stats finales LIVE + apercu + reactions ; parite prouvee ; ADDITIVES dans l'UI (flatBaseDamage, aussi forwarde au sidecar) + lunaires LC/LCrys ; SIDECAR PYTHON PAR DEFAUT dans l'apercu (opt-out IRMINSUL_ENGINE=local, repli TS documente, provenance honnete, preuve E2E badge moteur python-sidecar obligatoire) | latence spawn-par-appel du sidecar (acceptable apercu, a pooler si generalise) |
| Application web | 15 | 10 | 87 | high | Next.js 16.2.9 ; 9 surfaces (+ /diagnostic provenance moteur sanitizee) ; E2E 44/44 ; axe 0 critique ; resolution moteur unifiee (gele en desktop) | diagnostics UI ; desktop packaging |
| Application desktop | 10 | 12 | 84 | high | PROUVE bout-en-bout et REVALIDE (2026-07-20) avec le moteur a jour : rebuild sidecar (provenance commit=48f475a verifiee DANS l'app installee) + desktop:build + reinstall NSIS silencieuse + smoke installe TOUT VERT (7 routes 200, proxy.ts nonce POST/boot->403 x3, node lie au PID Tauri, zero orphelin x2, persistance DB, diagnostic sanitize) + cas d'erreur 4/4 chemin Unicode. L'app installee embarque lunaires+additives+sidecar-par-defaut. | MSI 1603 (per-machine sans elevation) ; non signe (SmartScreen) ; bind-race residuel accepte |
| Team builder et simulation | 15 | 15 | 95 | medium | Team Lab + reactions + rotations + comparateur + recommandations ; /simulation : vraies sims gcsim + squelette depuis equipe enrichi du scan GOOD (perso/arme/sets + stats artefacts reelles sans double-comptage) ; EXPORT rotation Team Lab -> actions gcsim (rotationToGcsimActions, verbes+groupage, ordre seulement honnete). Chaine complete equipe->config gcsim quasi-prete. 113 vitest | energie/cooldown fin ; buffs par action (modele analytique -> gcsim comble le gros du besoin) |
| Persistance | 5 | 8 | 82 | high | Prisma 6 + SQLite ; TeamRepository CRUD + importTeams TRANSACTIONNEL (rollback) ; export/import versionne irminsul-export/1.0 avec checksum | chemins %APPDATA% pour desktop |
| Design system et UX | 5 | 5 | 86 | medium | tokens OKLCH + primitives (Button/Card/Input/Select/ConfirmDialog/Toast/States/CharacterPicker) axe 0 critique ; BRAND_GUIDE.md ; LOGO Irminsul livre (SVG constellation-arbre degrade tokens, favicon /icon.svg, header logo+wordmark, animation legere reduced-motion safe, E2E) | icone desktop Tauri (PNG/ico a generer) ; Tooltip/Panel ; Tabs differe YAGNI |
| Tests et qualite | 5 | 4 | 84 | high | pytest 235 (ruff cable) ; vitest 106 (3 workspaces dans verify) ; E2E 48 (workflows reels + axe + moteur sidecar + toast) ; goldens croises TS<->Python ; garde manifest proxy ; ESLINT cable dans verify (typescript-eslint recommended, flat config, stock traite : 3 morts supprimes + convention underscore) | regles Next-specifiques eslint-config-next (extension future) ; rendu composants UI non teste unitairement (jsdom — couvert E2E) ; scripts .mjs hors lint |
| Packaging et deploiement | 3 | 2 | 74 | medium | NSIS installe/desinstalle/reinstalle PROUVE (per-user, sans admin) ; MSI produit mais 1603 sans elevation (preuve msi-install-1603.log) | MSI requiert admin ; non signe |
| Documentation et continuite | 2 | 2 | 75 | high | audit complet, DECISIONS, ARCHITECTURE, SESSION_HANDOFF, hook SessionStart | hook non encore enregistre dans settings |

_Recalcule : `python scripts/project_progress.py`._
