# Audit proxy/nonce Next 16 - 2026-07-08

Branche : `codex/proxy-nonce-security-audit`  
Base : `feat/irminsul-complete-redesign` @ `20c2a8b`  
Mode : audit read-only du code, aucun correctif applique.

## Perimetre inspecte

- `apps/web/src/proxy.ts`
- `apps/web/src/app/boot/route.ts`
- `scripts/smoke-desktop.mjs`
- `app/src-tauri/capabilities/default.json`
- `app/src-tauri/tauri.conf.json`
- `docs/desktop/DESKTOP_SECURITY_MODEL.md`
- Artefact de build Next genere par la verification obligatoire : `apps/web/.next/server/functions-config-manifest.json`

## Verifications executees

| Commande | Resultat | Preuve utile |
|---|---:|---|
| `npm run typecheck -w @irminsul/web` | PASS | `tsc --noEmit` termine avec code 0 |
| `npm run build -w @irminsul/web` | PASS | Next `16.2.9`, `Compiled successfully`, sortie `Proxy (Middleware)` |

Le build genere `apps/web/.next/server/functions-config-manifest.json`, qui confirme :

- runtime proxy : `nodejs` (`functions["/_middleware"].runtime`) ;
- matcher compile depuis `originalSource: "/((?!_next/static|_next/image|favicon.ico).*)"`.

## Findings

| ID | Severite | Fichier:ligne | Constat | Recommandation |
|---|---|---|---|---|
| PN-01 | OK | `apps/web/src/proxy.ts:15`, `.next/server/functions-config-manifest.json:5` | Le proxy lit `process.env["IRMINSUL_NONCE"]` et le build Next compile la fonction en runtime `nodejs`. La migration Next 16 n'introduit pas de contrainte Edge visible sur cette lecture d'env. | Garder un gate build qui verifie le manifest apres mise a jour Next. |
| PN-02 | OK | `apps/web/src/proxy.ts:18-23`, `.next/server/functions-config-manifest.json:8-9` | Le matcher couvre toutes les routes applicatives sauf `_next/static`, `_next/image` et `favicon.ico`; les methodes hors `GET/HEAD/OPTIONS` exigent un cookie `irm_nonce` exactement egal au nonce attendu. Les mutations Server Actions POST restent donc couvertes par design. | Aucun correctif code. Ajouter un test de non-regression sur le manifest si possible. |
| PN-03 | OK | `apps/web/src/app/boot/route.ts:11-26` | `/boot` refuse un nonce invalide par 403 et pose, si valide, un cookie `httpOnly`, `SameSite=Strict`, `path=/`. `secure=false` est coherent avec le loopback HTTP local. | Aucun correctif code. Le round-trip valide reste a prouver par smoke desktop. |
| PN-04 | LOW | `docs/desktop/DESKTOP_SECURITY_MODEL.md:13` | Documentation stale : le modele de securite parle encore de `middleware.ts` alors que le fichier reconnu par Next 16 est maintenant `proxy.ts`. Pas d'impact runtime, mais risque de confusion en revue de securite. | Claude peut corriger la doc en remplacant `middleware.ts` par `proxy.ts`. |
| PN-05 | RISK/LOW | `app/src-tauri/capabilities/default.json:6-9`, `docs/desktop/DESKTOP_SECURITY_MODEL.md:25-27` | La capability Tauri autorise toute origine `http://127.0.0.1:*` pour la fenetre `main`. C'est coherent avec le port dynamique Next, mais cela garde une surface large si une course au bind chargeait du contenu loopback inattendu. Les permissions exposees restent limitees (`core:default`, dialogues), donc ce n'est pas un blocage pour cette migration. | Claude doit conserver cette acceptation comme risque documente, ou envisager un durcissement futur si Tauri permet une origine plus precise au port runtime. |

## Faux-verts possibles du smoke desktop

- `scripts/smoke-desktop.mjs:111-119` teste bien les echecs critiques : `POST /` sans cookie, `POST /` avec cookie invalide, et `/boot` avec nonce invalide.
- Le test `/boot?n=mauvais-nonce` prouve le route handler `/boot`, pas le proxy, car les `GET` restent volontairement libres.
- Le smoke ne prouve pas le bootstrap valide `/boot` + cookie `httpOnly` + POST autorise : le nonce valide vit seulement dans l'env du serveur et la WebView.
- Le smoke doit etre relance apres un build desktop frais. Un smoke sur binaire ancien pourrait etre vert sans prouver le code courant.
- Le build web vert ne prouve pas le 403 desktop : il prouve seulement compilation, runtime nodejs et presence du proxy compile.

## Gaps de couverture

- Aucun E2E web ne force `IRMINSUL_NONCE` et ne verifie les 403 du proxy.
- Aucun test automatise ne compare le manifest Next attendu (`runtime=nodejs`, matcher original) apres upgrade Next.
- Le smoke couvre `POST /`, mais n'enumere pas toutes les routes Server Actions. Le matcher global rend ce choix raisonnable, mais le gap reste a connaitre.
- Les methodes `PUT/PATCH/DELETE` sont bloquees par le code actuel, mais ne sont pas explicitement testees.
- Le comportement 403 desktop reste le gate final, hors perimetre de cet audit read-only.

## A verifier par Claude avant merge

1. Triage de PN-04 et PN-05 : accepte, corrige, rejete ou differe.
2. Relancer un build desktop frais, reinstaller si necessaire, puis `scripts/smoke-desktop.mjs`.
3. Confirmer les trois assertions desktop : `POST sans cookie -> 403`, `cookie invalide -> 403`, `/boot invalide -> 403`.
4. Ne pas considerer le build web comme preuve du gate nonce desktop.
5. Verifier que toute correction eventuelle reste hors de cette branche d'audit ou fait l'objet d'une branche dediee.

## Conclusion

Aucune regression code bloquante trouvee dans la migration `middleware.ts` vers `proxy.ts`. Le point d'attention principal est la preuve runtime desktop : elle depend toujours du smoke installe, pas du build web. Un nettoyage documentaire mineur reste recommande.
