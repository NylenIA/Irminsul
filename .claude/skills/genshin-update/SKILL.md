---
name: Genshin Update
description: Met à jour les données locales Genshin, vérifie les commits et reconstruit l'index avant une analyse actuelle.
argument-hint: "[index-only|full]"
allowed-tools: Bash(uv run irminsul *), mcp__irminsul__*
---
Vérifie d'abord `irminsul_status`. Lance une mise à jour complète sauf si `$ARGUMENTS` demande seulement l'index. Résume les sources mises à jour, les échecs, l'âge final et les changements qui pourraient affecter la meta.
