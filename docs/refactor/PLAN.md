# PLAN — refonte progressive Irminsul (2026-06-29)

> **Aucune** de ces actions ne démarre avant la **fusion de la PR #3**. Branche dédiée
> `refactor/pro-ui-security` + PR séparée. Incréments réversibles, testés, mesurés. Pas de réécriture totale.
> Codex = réviseur **read-only** ; tout dev Codex futur = **worktree isolé** + fichiers autorisés explicites.

## Pré-requis (avant la branche refonte)
1. **Terminer R4** (revue Codex talents) — bloqué quota.
2. Fusionner PR #3 quand : R4 OK, 0 défaut critique/élevé, CI verte, app packagée validée, UID distant absent (✅).

## Priorisation (sévérité × valeur × réversibilité)
### Vague 1 — fondations sûres (faible risque)
- **Sécurité** : lockfile Python (S2) + `pip-audit`/`npm audit`/`cargo audit` en CI non bloquant (S5) ; threat model (S6).
- **Qualité** : extraire la logique de `QuickCalc.tsx` (A1/A2) en hooks + modules `domain` testés ; scinder `account.py` (A3).
- **Tests** : 1ers tests composant + a11y (axe) + clavier sur QuickCalc/Account (gap mesuré).

### Vague 2 — design system + UX
- `app/src/design/` (tokens + primitives) ; bibliothèque de composants (D1/D2) ; thèmes clair/sombre (D6).
- Accessibilité WCAG 2.2 AA mesurée (D3) ; responsive 1366×768 + zoom (D4) ; états standardisés (D5).

### Vague 3 — perf (sur mesure uniquement)
- Instrumenter démarrage/mémoire/latence sidecar (P1) ; virtualiser listes si mesuré (P2) ; lazy-load vues (P4).

## Méthode par incrément
baseline → audit → prioriser → prototype isolé → valider archi → implémenter → tester → **revue Codex (read-only)** →
corriger → **mesurer avant/après** → documenter → livrer. Critères d'acceptation + tests + migration claire par incrément.

## Garde-fous
- Ne jamais toucher les **zones mathématiques** (formules/données mécaniques) hors PR dédiée + revue.
- Aucune fausse donnée ; provenance préservée ; pas de régression fonctionnelle (test d'intégrité + suite existante).
- Chaque incrément : réversible (revert propre), borné, mesuré.

## Documents liés
`BASELINE.md` · `ARCHITECTURE.md` · `SECURITY_AUDIT.md` · `PERFORMANCE_AUDIT.md` · `DESIGN_AUDIT.md` ·
(à venir) `THREAT_MODEL.md` · `../project/SKILLS_AUDIT.md` · `../reviews/INCIDENT_engine_ts.md`.
