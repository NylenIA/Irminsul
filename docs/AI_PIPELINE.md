# Où est « l'IA » dans Irminsul

Question posée le 2026-07-27 : *« on pourrait le booster à l'IA ? créer une IA
experte pour la création/optimisation d'équipes, et un chef qui gère les
sous-agents et fait la connexion avec l'app »*. Voici l'architecture retenue,
avec ce qu'elle peut et ne peut pas faire.

## La contrainte à connaître

L'app est une application Windows locale et **gratuite**. Elle n'embarque pas
de modèle de langage : en embarquer un supposerait soit un service payant
appelé à chaque ouverture, soit un modèle local de plusieurs Go. Donc :

> **Ce qui décide dans l'app doit être déterministe.** Même box + même contenu
> = même réponse, hors-ligne, vérifiable ligne par ligne, gratuit.

Une IA qui « réfléchit » à chaque ouverture donnerait des réponses variables et
non reproductibles pour un joueur qui, lui, veut savoir *pourquoi* telle équipe.

## Les trois couches

### 1. Dans l'app — le moteur déterministe
- `lib/src/data/team_builder.dart` : construit les équipes depuis la box,
  applique les règles du contenu, affiche **chaque facteur du calcul**.
- `assets/data/character_tags.json` : ce que sait faire chaque perso.
- `assets/data/meta_teams.json > content` : règles du cycle (réactions
  amplifiées, éléments imposés, rôles favorisés), sourcées et datées.
- gcsim : le verdict chiffré (simulation frame par frame sur les vrais builds).

### 2. À la fabrique — les agents experts (Claude Code)
Ce sont eux, « l'IA », mais **en amont** : ils produisent et auditent ce que
l'app embarque, puis on prouve le résultat par simulation avant publication.

| Agent | Ce qu'il produit pour l'app |
|---|---|
| `team-architect` | tags des persos, poids du score, règles de contenu, cohérence des rotations |
| `theorycrafter` | mécaniques (gauge, ICD, énergie), archétypes, synergies |
| `dps-analyst` | configs et lectures gcsim, comparaisons de rotations |
| `live-data-researcher` | contenus du cycle en cours (Abîme, Théâtre, Carnage) et leurs dates |
| `account-optimizer` | lecture de la box réelle, priorités de montage |
| `leak-analyst` | persos non sortis, avec étiquetage et score de fiabilité |
| `source-auditor` | contrôle final : sources, dates, contradictions |

### 3. Le chef — l'orchestrateur
`irminsul-orchestrator` (`CLAUDE.md`) route selon la tâche :

- « pourquoi cette équipe / quelle équipe » → `team-architect` (+ `dps-analyst`
  pour le chiffre, `source-auditor` en sortie) ;
- « qu'y a-t-il dans le patch / le cycle » → `live-data-researcher` ;
- « que dois-je monter » → `account-optimizer` ;
- perso non sorti → `leak-analyst`, jamais présenté comme confirmé.

Règle permanente : **rien n'entre dans l'app sans preuve** — une source datée
(données de contenu) ou une simulation réussie (rotations, équipes).

## Boucle de mise à jour

```
agents (règles, contenus)  →  simulation gcsim (preuve)  →  meta_teams.json
        →  push GitHub  →  synchro OTA  →  app du joueur (sans réinstaller)
```

## Ce qui reste possible plus tard

Un **connecteur BYO-AI** dans l'app : le joueur colle sa propre clé d'API pour
poser des questions en langage naturel (« explique-moi pourquoi cette rotation »).
Optionnel, désactivé par défaut, et il ne décide de rien : les chiffres
resteraient ceux du moteur déterministe.
