# Utilisation de Duo dans Irminsul

## Objet

Duo relie Claude Code et Codex sans copier manuellement leurs messages. Il ne
fait pas partie du moteur Irminsul et ne modifie pas son architecture.

La configuration utilise `workflow.implementer: "auto"` :

- depuis Claude Code, Claude reste l’orchestrateur parent, Duo délègue la tâche
  à Codex, puis renvoie automatiquement la transmission de Codex à Claude ;
- depuis un terminal normal, Codex implémente et Claude relit ;
- depuis l’app Codex, Claude implémente avec `acceptEdits` et Codex relit en
  `read-only`, afin de conserver le sandbox parent.

## Fichiers ajoutés ou modifiés

- `duo.config.json` : commandes des agents, rôles automatiques et limites de
  sécurité. Il ne contient aucun secret.
- `.gitignore` : ajout de `.duo/`.
- `.duo/` : journaux et états locaux de sessions. Ce dossier est ignoré par
  Git et peut contenir des extraits de prompts ou de code ; ne jamais le
  committer.
- `docs/project/DUO_USAGE.md` : ce guide.

Les jetons et sessions d’authentification restent dans les emplacements privés
de Claude Code et Codex, hors du dépôt.

## Installation et diagnostic

Depuis PowerShell :

```powershell
cd "C:\Users\akuon\IA Genshin\Irminsul-AI-Claude-Code"

# Initialiser seulement si nécessaire
if (-not (Test-Path .\duo.config.json)) {
    duo init
}

duo doctor
```

Résultat observé le 28 juin 2026 :

```text
Projet : C:\Users\akuon\IA Genshin\Irminsul-AI-Claude-Code
✓ Configuration: C:\Users\akuon\IA Genshin\Irminsul-AI-Claude-Code\duo.config.json
✓ Dépôt Git: détecté
✓ Claude Code: 2.1.195 (Claude Code) (C:\Users\akuon\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe)
✓ Codex CLI: codex-cli 0.142.3 (C:\Users\akuon\AppData\Local\OpenAI\Codex\bin\aec6b7c6fcdfb66a\codex.exe)
✓ Rôles: claude implémente, codex relit
```

La ligne des rôles décrit le contexte du terminal qui exécute `doctor`. Quand
Claude Code lance `duo run`, le mode « Claude parent » prend la priorité et
Codex devient l’agent délégué.

Vérifications d’authentification, sans afficher ni enregistrer de jeton :

```powershell
claude.cmd auth status

$codexCli = Get-ChildItem `
    "$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe" `
    -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
& $codexCli.FullName login status
```

État vérifié : Claude Code connecté via `claude.ai` avec un abonnement Pro ;
Codex connecté via ChatGPT.

## Lancer une tâche

Depuis PowerShell :

```powershell
duo run "Décris précisément la tâche, son périmètre et les vérifications attendues."
```

Depuis une session Claude Code, demander par exemple :

```text
Dans ce dépôt, lance via Bash :
duo run "Analyse ce problème et applique uniquement la correction demandée."
Attends la fin, puis vérifie la transmission de Codex et le diff Git.
```

Claude exécute la commande, Duo transmet la tâche à Codex et le résultat revient
dans la même session Claude. Aucun copier-coller de messages n’est nécessaire.

Commandes de suivi :

```powershell
duo sessions
duo show <identifiant-de-session>
```

## Validation effectuée

Le pont réel a été testé depuis ce dépôt avec une tâche de transport bornée et
sans lecture ni modification de fichier :

```text
Claude Code → duo run → Codex → Duo → Claude Code
```

Session Duo : `2026-06-28T11-56-07-339Z-56201af4`

Réponse Codex reçue automatiquement par Claude : `DUO_BRIDGE_OK`.

## Sécurité

- Ne jamais ajouter de clé API, jeton, cookie ou fichier d’authentification au
  dépôt.
- Conserver `.duo/`, `.env` et `.claude/settings.local.json` hors de Git.
- Examiner `git diff` et les tests avant tout commit.
- Utiliser une tâche strictement bornée ; Duo ne remplace pas la revue humaine.
- Ne pas utiliser `danger-full-access`. La configuration Irminsul conserve
  `workspace-write` pour Codex et les modes restrictifs adaptés au parent.
