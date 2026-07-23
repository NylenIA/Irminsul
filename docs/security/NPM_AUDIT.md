# Audit des dépendances npm (web monorepo)

> Politique : ne JAMAIS lancer un downgrade cassant automatique (`npm audit fix --force`).

## Vulnérabilités
| Package | Type | Advisory | Chemin | Exploitabilité réelle | Correctif | Décision |
|---|---|---|---|---|---|---|
| postcss `<8.5.10` | transitif | GHSA-qx2v-qp2m-jg93 (XSS via `</style>` non échappé dans le CSS stringify) | `next` → `postcss` | **Faible** : concerne la sortie du *stringifier* PostCSS sur du CSS non fiable ; notre CSS est de confiance (build-time, pas d'entrée utilisateur) | `npm audit fix --force` **rétrograderait Next.js** (cassant) | **ACCEPTÉ + surveillé** : attendre une version de Next embarquant postcss ≥ 8.5.10. Pas de downgrade. |

(Re-mesurer après ajout de Prisma/Vitest : `npm audit`. Mettre à jour ce tableau si de nouvelles apparaissent.)

## Scripts d'install bloqués (npm 11 allow-scripts)
- `@prisma/engines`, `prisma`, `esbuild`, `sharp` : postinstall **non exécutés** par défaut (npm 11).
- **Prisma** : le moteur de requête doit être disponible à l'exécution. Si les tests Prisma échouent en « engine », autoriser **officiellement** : `npm approve-scripts @prisma/engines prisma` (sources Prisma auditées), puis relancer. Documenté ici plutôt qu'autorisé en aveugle.
- **sharp** : utilisé par `next/image` pour l'optimisation. Le build Next a réussi **sans** ce script. Décision : non bloquant en dev ; autoriser via méthode officielle (`npm approve-scripts sharp`) seulement si l'optimisation d'images réelle en a besoin.

## Principe
Aucun binaire opaque auto-téléchargé. Toute autorisation de script passe par la commande npm officielle, documentée, package par package.
