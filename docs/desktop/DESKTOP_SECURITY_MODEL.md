# Modèle de sécurité desktop — nonce loopback & cycle de vie des processus

## Nonce éphémère (correctif audit M3)
**Menace** : un processus local tiers (même session utilisateur, non élevé) joint le serveur
Next loopback et déclenche des MUTATIONS (Server Actions POST : équipes, import) dans les
données de l'utilisateur ; ou détourne le port par une course au bind.

**Flux implémenté**
1. À chaque lancement, Tauri génère 32 octets crypto (`getrandom`) → nonce hex 64.
2. Transmis UNIQUEMENT : env `IRMINSUL_NONCE` du process Next (mémoire) + navigation initiale
   `GET /boot?n=<nonce>` de la WebView.
3. `/boot` (route handler) compare, pose un cookie **httpOnly SameSite=Strict** puis redirige `/`.
4. `middleware.ts` : toute requête **POST** (mutations) sans cookie exact → **403**. GET/HEAD
   libres (rendu, assets, health check — lecture locale non sensible).
5. Rotation : nouveau nonce à chaque lancement ; jamais loggé, jamais persisté, absent de la base.

**Pourquoi les GET restent libres** : le rendu des pages ne modifie rien et la donnée locale
n'a pas de secret ; bloquer les GET casserait health check et assets sans gain réel.

**Limites documentées**
- Le nonce transite une fois en query `/boot` : Next standalone (production) ne journalise pas
  les URLs ; risque résiduel = un observateur du process (déjà au niveau de l'utilisateur).
- Un malware exécutant du code dans la session peut lire l'env du process : hors modèle —
  ce nonce bloque l'accès réseau local opportuniste, pas un hôte compromis.
- Course au bind (fenêtre libération→bind) : le hijacker ne connaît pas le nonce → la WebView
  poserait un cookie chez lui mais les mutations réelles n'iraient nulle part ; risque réduit
  à un déni local, accepté.

## Job Object Windows — évaluation (T5)
**Décision : NON implémenté pour l'instant, conservé en amélioration.**
Justification par tests : la fermeture normale (WM_CLOSE → `RunEvent::Exit` → kill+wait) et
l'échec post-spawn (kill+wait+clear) laissent **zéro orphelin**, prouvé sur binaire production
ET installation NSIS (2 fermetures chacun, liaison stricte PID parent→enfant). Le seul trou est
le **kill forcé** (`taskkill /F`) du process Tauri : l'enfant Node survivrait jusqu'à extinction
manuelle. Un Job Object (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) fermerait ce trou mais exige du
code unsafe/win32 supplémentaire ; le rapport bénéfice/risque est faible pour un outil local
mono-utilisateur. Réévalué si un crash réel du superviseur est observé.
