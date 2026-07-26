---
name: reference-local-paths
description: Où se trouvent, hors dépôt, le GOOD réel du joueur et le moteur gcsim qui sert à valider les rotations
metadata:
  type: reference
---

Ressources **hors dépôt** (gitignorées ou temporaires) utilisées pour valider
sur données réelles :

- **Export GOOD du joueur** : `E:\Bureau\genshinData_GOOD_2026_07_24_16_44.json`
  (Inventory Kamera). C'est la vérité terrain pour tout test de matcher, d'ER
  ou de simulation « sur SA box ». Vérifier la date du fichier : il en produit
  de nouveaux à chaque scan.
- **Moteur gcsim de validation** :
  `%LOCALAPPDATA%\Temp\irm-verify\app\gcsim.exe` — binaire extrait de la
  release `dev-latest` (donc **exactement** celui de son app, avec Iansan et
  Varka intégrés). En Git Bash : `"$LOCALAPPDATA/Temp/irm-verify/app/gcsim.exe"`.
  Si absent, le re-télécharger depuis la release plutôt que de simuler avec un
  gcsim officiel (les persos patchés manqueraient).
- **Livraison de l'app** : release GitHub `dev-latest` du repo `NylenIA/Irminsul`
  (branche `flutter-app`), publiée par le workflow *Build Windows* (~8 min).

**Commandes utiles** (depuis `irminsul_app/`) :
`python tool/validate_templates.py <gcsim.exe> [GOOD] [--only id1,id2] [--json out.json]`
puis `python tool/update_meta_db.py`. Voir [[project-roster-goals]] et
[[current-content-rigor]].
