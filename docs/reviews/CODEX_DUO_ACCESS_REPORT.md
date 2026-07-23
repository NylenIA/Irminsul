# Rapport d'accès Codex via Duo — 2026-07-10

But : vérifier **réellement** ce que Codex peut faire quand Claude Code le lance lui-même
(via Duo / `codex exec`), sans rien affirmer sans preuve. Toutes les lignes ci-dessous
proviennent de commandes exécutées cette session.

## 1. Outils installés (vérifiés)
| Outil | Version | Preuve |
|---|---|---|
| Duo | `duo-agents 0.3.1` | `duo --version` |
| Codex CLI (PATH) | `codex-cli 0.142.4` | `codex --version` |
| Codex CLI (utilisé par Duo) | `0.144.0-alpha.4` (`…\AppData\Local\OpenAI\Codex\bin\…`) | `duo doctor` |
| Claude Code | `2.1.195` | `duo doctor` |

## 2. Duo (vérifié)
- Commandes : `duo run "<tâche>" [--repairs] [--dry-run]`, `duo send/ask --to claude|codex|both`, `duo status`, `duo agents`, `duo pause/resume`, `duo doctor`, `duo watch/ui/dashboard`.
- `duo doctor` : **rc 0** — Node 24.18, config détectée, `.duo/` inscriptible et gitignoré, dépôt Git OK.
- **Rôles configurés** : « codex implémente, claude relit » (conforme au protocole).
- `duo.config.json` : `codexSandbox = "workspace-write"`, `skipGitRepoCheck = false`, `maxHandoffChars = 24000`, `repairCycles = 1`.
- Preuve d'usage antérieur : `.duo/runtime/codex-audit-*.md` (nombreux reçus d'audits Codex réels).

## 3. Codex CLI (vérifié)
- **Auth réelle** : `codex login status` → « Logged in using ChatGPT » (rc 0).
- **Exécution non-interactive** : `codex exec [OPTIONS] [PROMPT]` (alias `e`) — prompt en arg ou stdin.
- **Modèle réel** : `model: gpt-5.5` (provider `openai`), observé dans l'en-tête d'un run `codex exec`.
- **Sandbox** : `-s <read-only | workspace-write | danger-full-access>`. Portée observée en workspace-write : `[workdir, /tmp, $TMPDIR]`. `approval: never` (autonome dans la sandbox).
- Autres flags utiles : `-C <dir>` (cwd), `-o <fichier>` (dernier message), `--json`, `-c clé=valeur` (override, ex. `-c model_reasoning_effort="low"`), `--skip-git-repo-check`.
- **Effort de raisonnement** : défaut `xhigh` (très lent), abaissable via `-c model_reasoning_effort="low"` (vérifié : l'override est bien appliqué).

## 4. Ce qui MARCHE (prouvé)
- Claude peut **invoquer `codex exec`** non-interactivement, dans un **worktree Git isolé** (`git worktree add`), avec sandbox et cwd contrôlés. Codex démarre, s'authentifie, charge `gpt-5.5`, comprend une mission bornée et annonce le respect du périmètre.
- Le cycle **desktop-app Codex** (lancé par Nylen) est **prouvé** : toutes les missions précédentes (migration proxy, harden E2E, audit nonce, wire-verify) ont produit des diffs réels et corrects via l'app Codex.

## 5. Ce qui NE MARCHE PAS aujourd'hui (prouvé, honnête)
- **Blocage `codex exec` en sandbox** : dès que Codex tente d'exécuter une commande shell (ex. `Get-Content package.json`), le helper de sandbox Windows échoue :
  `windows sandbox: orchestrator_helper_exit_nonzero: setup helper exited with status Some(-1073741502)`.
  `-1073741502` = **`0xC0000142` (STATUS_DLL_INIT_FAILED)** — même classe d'erreur que le spawn imbriqué de `npm run desktop:build` (pression desktop-heap / init de process sous forte charge : MCP nodes + app Codex + session Claude).
- Conséquence : le **smoke automatisé `codex/duo-access-smoke` n'a PAS abouti** (aucun reçu écrit). Le smoke Duo/Codex piloté par Claude **n'est donc PAS validé** sur cette machine pour l'instant.
- **Skills / sous-agents** : Codex CLI **n'a pas** accès aux sous-agents ni aux skills de Claude Code (ils sont côté Claude). → à transmettre en **context pack** texte.

## 6. Pont mis en place
- `.duo/context-packs/codex-default.md` (gitignoré) : rôle, règles de sécurité, **bloc Contraintes d'inspection standard**, gates, chemins Windows backslash. À joindre à chaque mission.

## 7. Modes sûrs recommandés
1. **Chemin fiable AUJOURD'HUI** : missions via l'**app Codex desktop** (lancées par Nylen), Claude prépare briefing + context pack, relit le diff, lance les gates, intègre, **no push sans accord**. C'est le seul chemin prouvé fonctionnel.
2. **`codex exec` piloté par Claude** : à réactiver **seulement après résolution** du blocage sandbox `0xC0000142` (réduire la charge de process, ou investiguer le helper sandbox Windows de Codex, ou tester la version 0.144-alpha via Duo). L'option `--dangerously-bypass-approvals-and-sandbox` contournerait le helper mais est **déconseillée** (exécution non sandboxée) — hors principe « pas d'accès incontrôlé ».
3. Toujours : **worktree isolé + no-push + revue Claude obligatoire**.

## 8. Verdict
- Claude **peut techniquement lancer Codex** (auth, modèle, sandbox, worktree vérifiés).
- Mais l'exécution sandboxée de commandes échoue (`0xC0000142`) → **la délégation CLI autonome n'est pas encore fiable**.
- **Reco** : continuer via l'**app Codex** (prouvée) jusqu'à correction du helper sandbox ; ne lancer aucune mission produit Codex en CLI tant que le smoke n'est pas vert.
