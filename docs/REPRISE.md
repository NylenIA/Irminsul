# Reprise de session — état au 2026-07-28

Document à lire en premier dans une nouvelle conversation. La liste des
demandes vit dans `docs/BACKLOG.md` ; ici, c'est l'état technique et les
pièges à connaître.

## Où en est le projet

**App Irminsul** (Flutter Windows) — theorycrafter Genshin qui croise la box
réelle du joueur avec la méta et simule les équipes via gcsim.

- Dépôt de code **public** : `NylenIA/Irminsul`, branche `flutter-app`.
  Dernier commit poussé : `2a7164b`, build ✅.
- Dépôt **privé** : `NylenIA/irminsul-prive` — box, équipes créées, exports
  GOOD, analyses de compte, mémoire de l'assistant. **Règle posée par le
  joueur : tout ce qui est privé va là-bas, jamais dans le public.**
- Livraison : release GitHub `dev-latest` → `Irminsul-windows.zip`
  (app + moteur gcsim), reconstruite chaque nuit à 06 h 30 UTC.

## Ce qui a été fait dans la session qui se termine

### Persos ajoutés au moteur gcsim (ils n'existent pas en amont)

| Perso | État du kit |
|---|---|
| **Zibai** | multiplicateurs, passifs (Moonsign, A1, A4), C2, arme signature ✅ · C1 tronquée dans les données |
| **Illuga** | multiplicateurs, Moonsign, A4 ✅ · A1 tronqué |
| **Linnea** | multiplicateurs, Moonsign, A1 (RÉS Geo −15 %), A4, C2 ✅ · C1 tronquée |
| **Sandrone** | multiplicateurs, A4, C2 ✅ · **passif innée bloqué** (voir A5) |

Armes ajoutées : **A Teaspoon of Transcendence** (Sandrone),
**Lightbearing Moonshard** (Zibai, passif implémenté).

### Effet mesuré sur la BiS de Zibai (Zibai/Illuga/Linnea/Columbina)

Même rotation, équipement réel du joueur, binaire publié :

| Étape | DPS |
|---|---|
| multiplicateurs seuls | 19 170 |
| + passifs de Zibai | 22 793 |
| + C2 et arme de Zibai | 24 680 |
| + kits d'Illuga et Linnea | **27 592** |

### Autres corrections notables

- La liste des persos simulables (`assets/data/gcsim_chars.json`) est
  désormais **générée en CI depuis le moteur compilé** — avant, elle était
  écrite à la main et l'app affichait « pas encore simulable » à tort.
- Substitutions de persos appliquées aux textes de rotation, alias compris
  (le fameux « Kokomi E » alors que Barbara jouait).
- Optimiseur d'équipes reconstruit sur des **archétypes réels** (plus de
  combinaisons inventées) ; conditions des réactions lunaires respectées.

## Le point de désaccord à garder en tête

Le joueur mesure **~200 000 DPS en UGC après la 2ᵉ rotation** ; gcsim donne
une **moyenne sur 90 s** incluant la montée en puissance. Les deux chiffres
peuvent être justes. Deux chantiers en découlent :

1. **A6** — afficher aussi le DPS en régime établi, pour comparer ce qui est
   comparable ;
2. il reste de vrais trous de kit (voir ci-dessous) : l'écart n'est pas
   seulement méthodologique.

## Prochaines étapes, dans l'ordre

1. **A5 — Stellar-Conduct dans le cœur du moteur.** Bloquant pour Sandrone :
   son passif innée convertit les Supraconducteurs de l'équipe en
   Stellar-Conduct, et le cycle d'Abîme en cours amplifie justement ces deux
   réactions. **Condition pour démarrer : obtenir les valeurs depuis une
   source vérifiable** (tables du jeu via `tool/datamine.py`, ou KQM) — les
   articles de leak ne suffisent pas.
2. **A1/A2 — Lohen + son arme Disaster and Remorse**, puis Nefer, Kachina,
   Ifa, Jahoda, Prune.
3. **B5/B6/B7 — rotations pré-faites** proposées selon l'équipe détectée, et
   « voilà ce que tu dois faire » pour les équipes créées.
4. **A6 — régime établi** (voir ci-dessus).
5. **D1/D2/D3 — dashboard utile, onglet builds par perso, interrupteurs
   on/off** sur les artefacts et stats.
6. **C2/C3 — stratégie et images par boss.**
7. **E3 — mise à jour de l'app depuis l'app** (aujourd'hui : seules les
   données se mettent à jour seules).

## Outils et méthode (à réutiliser tel quel)

Depuis `irminsul_app/` :

```bash
python tool/datamine.py <Perso>              # données exactes du jeu
python tool/gen_gcsim_char.py <Perso>        # fichier Go des données
python tool/gen_gcsim_weapon.py "<Arme>"     # idem pour une arme
python tool/patch_gcsim_chars.py <gcsim-src> # installe nos persos/armes
python tool/check_keys_alignment.py <gcsim-src> <clés...>
python tool/dart_sanity.py lib               # remplace flutter analyze en local
python tool/simulate_builder.py <GOOD> <mode> [--sim <gcsim.exe>]
```

### Pièges déjà rencontrés — ne pas les refaire

- **« build success » ne prouve rien.** Le workflow a des replis en cascade :
  si nos persos ne compilent pas, ils sont retirés et le build « réussit »
  sans eux. La seule preuve, c'est une **simulation avec le binaire publié**.
- Vérifier que le zip téléchargé date **d'après** la fin du run (sinon on
  teste l'ancien binaire — déjà arrivé).
- Console Windows en cp1252 en CI : pas de caractère hors cp1252 dans un
  `print()` Python, sinon le script plante et on perd les persos.
- Un dossier d'arme sans `func NewWeapon` casse tout le lot (garde-fou
  ajouté dans le patcher).
- Dans cette version de gcsim, un hook d'événement ne renvoie **rien**
  (`func(args ...any)`), et le test du perso actif est `c.Player.Active()`.
- Les tableaux de multiplicateurs sont nommés d'après le **numéro de
  paramètre** cité dans le libellé, pas d'après la position du libellé.

### Environnement

- Dossier de travail : `E:\IA Genshin`, dépôt dans
  `E:\IA Genshin\Irminsul-AI-Claude-Code`.
- **Ni Flutter ni Go en local** : la CI compile tout. Python 3.11+, Git et
  `gh` suffisent.
- GOOD réel du joueur et moteur de validation : voir le dépôt privé
  (`memoire/` et `app/`).

## Règles permanentes

- Toujours partir de la **méta** (sources datées, KQM en priorité) avant de
  coder une équipe. Ne jamais inventer une composition.
- **Kit complet** pour tout perso ajouté : multiplicateurs, passifs,
  constellations, passif d'arme.
- Ne jamais présenter un **leak** comme confirmé ; ne pas implémenter des
  valeurs qui n'existent que dans des articles de leak.
- Marquer explicitement ce qui est approximé (frames, particules, effets
  tronqués) et **sous-estimer plutôt que surestimer**.
