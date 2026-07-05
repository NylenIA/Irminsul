# Triage — audit Codex read-only Import/Export + repo transactionnel + provenance

> Reçu : `.duo/runtime/codex-audit-io.md` (gpt-5.4-mini, worktree isolé — non détourné).
> Politique reçus-tardifs appliquée (attente bornée → triage à réception).

| # | Sévérité | Finding | Décision | Correction / Test |
|---|---|---|---|---|
| 1 | **Medium** | Schéma non strict : champs inconnus conservés, `checksumOf` parcourait récursivement l'objet **brut** → JSON profond/large sous 2 Mo pouvait saturer CPU/stack ; cap 500 absent du chemin preview. | **accepted + fixed** | scan de profondeur **linéaire avant parse** (≤ 30 niveaux) ; bornes structurelles (≤ 500 équipes, 1..4 membres, noms ≤ 200) ; `sanitizeTeams` whitelist stricte des clés à tous les niveaux ; checksum calculé sur la **copie sanitizée** uniquement. 3 tests |
| 2 | **Medium** | Checksum contournable (ignoré si absent/non-chaîne) ; FNV-1a n'est pas anti-tamper. | **accepted + fixed (périmètre documenté)** | checksum **REQUIS** pour 1.0, format exact `[0-9a-f]{8}` validé ; omission ⇒ rejet. FNV conservé avec périmètre explicite : **détection de corruption**, pas anti-tamper crypto — le fichier est une donnée locale de l'utilisateur, revalidée structurellement à l'import, sans secret ni frontière de confiance ; un HMAC n'apporterait pas de garantie utile sans gestion de clé. 1 test |
| 3 | **Low** | Preview (first-wins, noms bruts) ≠ persistance (trim + last-wins) → aperçu ≠ résultat écrit sur doublons/espaces. | **accepted + fixed** | politique unique : noms trimés en sanitization ; `planImport` marque les occurrences **non finales** comme ignorées (la dernière gagne, identique au `Map` d'`importTeams`). 1 test |

## Vérifications positives (confirmées par l'audit)
Parse sans exécution ✅ · borne de taille avant parse (client + serveur) ✅ · **atomicité `importTeams`
réelle** (transaction, validation avant écriture, pas de corruption partielle) ✅ · borne 500 côté
apply ✅ · **aucune fuite de chemin** (provenance = git_commit + version Python ; io-actions = nom de
fichier/contenu/compte) ✅ · pas de chemin arbitraire du frontend (`<input type=file>`) ✅ ·
Unicode/vide couverts ✅.

## Point resté ouvert (honnête)
« Version future/ancienne gérée : non » — exact : seule 1.0 existe, `tryMigrate` est un point
d'extension. Une version future est **rejetée proprement** (`unsupported_version`), c'est le
comportement voulu tant qu'aucune 1.1 n'existe. Réévalué à la première évolution de format.

## Gates post-correctif
vitest **81** (12 io dont 5 régression) · build+TS PASS · E2E **40/40** · pytest 220 (inchangé).
