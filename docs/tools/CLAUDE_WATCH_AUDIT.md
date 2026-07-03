# Audit « Claude Watch » — verdict : nom non prouvé, candidat réel identifié, PAS installé

> Mission : vérifier avant d'installer. Vérifié le 2026-07-02.

## Découverte (preuves)
| Source | Résultat |
|---|---|
| npm `claude-watch` / `@anthropic-ai/claude-watch` | **404 — n'existe pas** |
| CLI `claude --help` (watch/video) | **aucune commande** native |
| Skills/plugins locaux | aucun |
| Web | **« Claude Watch » n'est PAS un produit Anthropic.** Candidat réel le plus proche : [`bradautomates/claude-video`](https://github.com/bradautomates/claude-video) — plugin Claude Code tiers, commande `/watch` (télécharge la vidéo, extrait des frames, transcrit, fournit le tout à Claude). Alternative : MCP `yt-analysis` (YouTube). |

## Audit du candidat `bradautomates/claude-video`
- Réel, actif (dernier push 2026-07-01), LICENSE présent, structure plugin (`.claude-plugin`, `AGENTS.md`, skills).
- **Statut : `candidate — NON installé`.** Conditions §7 non toutes prouvées : contenu des scripts non audité
  (l'outil **télécharge des vidéos** → accès réseau, probable yt-dlp ; périmètre d'écriture à vérifier).
  Installer un outil qui télécharge du contenu externe sans audit de ses scripts violerait la politique projet.
- **Décision** : installation seulement après (1) lecture des scripts du plugin, (2) confirmation utilisateur
  que c'est bien CET outil qu'il visait sous le nom « Claude Watch ».

## Fallback local (§10) — état
Pipeline auditable prévu : `ffprobe (métadonnées) → ffmpeg (frames ciblées) → manifest horodaté → analyse
Claude des frames`. **Bloqueur : ffmpeg/ffprobe absents de la machine** (vérifié). 
→ Action utilisateur unique si voulue : `winget install Gyan.FFmpeg` (ou confirmer l'audit de claude-video).
Le skill interne `irminsul-video-analysis` sera créé après l'un des deux déblocages — il ne sera jamais
présenté comme « Claude Watch ». Vidéos : traitement local, jamais commitées, jamais uploadées sans accord.

## Cas d'usage Irminsul (une fois débloqué)
Analyse des captures E2E Team Lab (transitions, reduced-motion, pop-ups Windows, fluidité, mobile vs desktop) —
en complément des tests automatisés, jamais en remplacement.
