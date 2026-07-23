# Matrice de routage systémique des skills (plan)

> « Systémique » = chaque mission moyenne/grande passe par un routeur qui sélectionne les skills pertinents.
> ⚠️ Aujourd'hui seuls **frontend-design, skill-creator, webapp-testing** sont disponibles ; les lignes
> citant un skill **[absent]** sont des cibles, applicables une fois le skill réellement installé.

| Type de mission | Pipeline de skills |
|---|---|
| Moyenne/grande (défaut) | senior-architect[absent] → skill domaine → code-reviewer[absent] → senior-qa[absent]/**webapp-testing** |
| Nouveau comportement / bugfix | tdd-guide[absent] → domaine → code-reviewer[absent] → senior-qa[absent] |
| Backend / données / moteur | senior-backend[absent] + senior-architect[absent] + senior-security[absent] si données → tdd-guide[absent] → review |
| Frontend Next.js/Tauri | senior-frontend[absent] + **frontend-design** + ui-ux-pro-max[absent] + ui-styling[absent] + design-system[absent] + frontend-design-review[absent] + **webapp-testing** |
| Identité visuelle | design[absent] + brand[absent] + design-system[absent] + ui-styling[absent] + **frontend-design** + frontend-design-review[absent] |
| Sécurité / MCP / hooks / DB | senior-security[absent] + senior-architect[absent] + domaine + code-reviewer[absent] + senior-qa[absent] |
| Présentation / doc visuelle | slides[absent] + brand[absent] + design[absent] + banner-design[absent] |

## Garde-fous
- Un skill `untrusted`/`candidate` démarre en **SHADOW / ADVISORY** : sa sortie est revue avant application.
- Un skill n'écrit pas hors de son domaine sans revue.
- Le routeur réel ne peut sélectionner que des skills **présents** ; les `[absent]` sont ignorés jusqu'à installation.
