# Irminsul (app Flutter)

App native de theorycrafting Genshin Impact. Voir [`../docs/VISION.md`](../docs/VISION.md)
et [`../docs/ROADMAP.md`](../docs/ROADMAP.md).

## Étape 1 (en cours)
Socle Flutter + Riverpod + go_router, thème « Helios », i18n FR/EN,
écran d'onboarding (import GOOD / UID Enka), CI GitHub Actions → `.exe` Windows.

## Build
Le build est fait **dans le cloud** par GitHub Actions (voir
`.github/workflows/build-windows.yml`). Les dossiers de plateforme (`windows/`, etc.)
sont générés en CI par `flutter create` et ne sont pas versionnés.

En local (si Flutter installé) :

```bash
flutter create --platforms=windows --project-name irminsul --org com.nylenia .
flutter pub get
flutter run -d windows
```
