# Incident — suppression de `app/src/engine.ts` hors mission (2026-06-29)

## Résumé
`app/src/engine.ts` a disparu du disque **entre un build frontend vert et un `git add`**, et le
commit `fa41071` a embarqué sa suppression (poussée sur `origin/feat`). Détecté immédiatement
(diff `delete mode app/src/engine.ts`), restauré à l'identique (`dd71f19`), build re-vert.

## Investigation (faits)
- **Hooks Git** : aucun hook custom (seulement `.sample`). → écarté.
- **Tâches planifiées** : seule `\FanControl` (matériel), sans rapport. La tâche Duo
  `DuoControlCenter-bf3cadcfcd` a été **désactivée**. → écarté comme déclencheur direct.
- **Processus** : **8 `Codex.exe` orphelins** tournaient encore ~6 h après les sessions duo
  R1–R3 (19:39–19:51 le 28/06), au moment de la restauration (~01:47 le 29/06). Terminés.
- **Config Duo** : `safety.codexSandbox = "workspace-write"` → un Codex (même orphelin) **pouvait
  écrire/supprimer** dans le workspace. `.duo/integration-check` montre que Duo lance aussi des
  instances **Claude** (`claude-launch`) — agents capables d'éditer.

## Cause probable (honnête)
Aucun log ne dit littéralement « engine.ts supprimé ». Mais la combinaison **Codex orphelins +
sandbox `workspace-write`** rend la suppression hors-mission possible. C'est la cause la plus
plausible ; impossible de prouver le processus exact a posteriori. Facteur aggravant : le sandbox
en écriture était appliqué même pour des missions de **revue** (qui n'ont besoin que de lecture).

## Mitigations appliquées
1. **Isolation définitive** : `duo.config.json` → `codexSandbox: "read-only"`. Codex ne peut
   désormais **plus jamais** modifier les fichiers (il sert uniquement de réviseur indépendant).
   Toute mission d'implémentation déléguée devra relever ce niveau de façon explicite et bornée.
2. **Anti-double-exécution** : verrou `.irminsul/locks/resume.lock` posé pendant les opérations
   sensibles ; terminaison des processus agents orphelins avant toute réécriture/commit critique.
3. **Test de non-régression** : `tests/test_repo_integrity.py` échoue si un fichier CRITIQUE
   (engine.ts, modules moteur, données mécaniques, pont Rust, scripts) disparaît ou se vide →
   détection immédiate dans `validate.sh` et la CI, avant tout commit/CI vert trompeur.
4. **Scheduler Duo** : laissé **DÉSACTIVÉ**. Le scheduler lance des agents (Claude/Codex) ; tant
   que ces lancements ne sont pas garantis bornés/lecture seule, il reste désactivé.

## Conditions de réactivation du scheduler
- `codexSandbox=read-only` confirmé (fait) ; ET
- les lancements programmés d'agents sont scopés à des missions bornées **sans auto-édition** des
  fichiers Irminsul (à vérifier dans le wrapper `.duo/scheduler-resume.cmd` / `duo scheduler tick`) ;
- puis `duo scheduler enable` (décision explicite de l'utilisateur).
