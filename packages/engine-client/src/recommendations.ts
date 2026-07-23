/**
 * Moteur de recommandations `recommendations/1.0` — DÉTERMINISTE et EXPLICABLE.
 * Fondé UNIQUEMENT sur les données réelles du compte (`PlayerCharacterBuild` : niveau, arme,
 * artéfacts, talents, constellation, champs `missing`) et les équipes sauvegardées.
 * Aucun classement opaque, aucun chiffre d'impact inventé, aucune donnée web non sourcée.
 * Méthode : éliminer l'invalide → évaluer la complétude → recommander le prouvable → expliquer.
 */
import type { PlayerCharacterBuild } from "./player-build";

export const RECOMMENDATIONS_CONTRACT_VERSION = "recommendations/1.0";

export type RecommendationObjective =
  | "highest_complete_dps"
  | "balanced_team"
  | "low_investment"
  | "survivability"
  | "reaction_focus"
  | "improve_current_team"
  | "data_quality";

export type RecommendationType =
  | "team"
  | "rotation"
  | "character_upgrade"
  | "weapon"
  | "artifact"
  | "talent"
  | "energy"
  | "survivability"
  | "data_quality";

export interface RecommendationItem {
  type: RecommendationType;
  title: string;
  explanation: string;
  evidence: string[];
  tradeoffs: string[];
  /** Impact QUALITATIF uniquement (jamais un chiffre inventé). */
  expectedImpact: "qualitatif" | "améliore la fiabilité du calcul" | "non quantifié";
  confidence: "high" | "medium" | "low";
  requiredData: string[];
}

export interface RecommendationRequest {
  objective: RecommendationObjective;
  availableCharacterIds: string[];
  currentTeamId?: string;
  constraints?: {
    requiredCharacterIds?: string[];
    excludedCharacterIds?: string[];
    maxInvestmentLevel?: "low" | "medium" | "high";
  };
}

export interface TeamForReco {
  id: string;
  name: string;
  members: string[];
}

export interface RecommendationResult {
  contractVersion: string;
  objective: RecommendationObjective;
  recommendations: RecommendationItem[];
  assumptions: string[];
  provenance: { source: string; importedAt?: string }[];
  missingData: string[];
  confidence: "high" | "medium" | "low";
}

const OBJECTIVE_LABELS: Record<RecommendationObjective, string> = {
  highest_complete_dps: "DPS fiable maximal",
  balanced_team: "équipe équilibrée",
  low_investment: "faible investissement",
  survivability: "survie",
  reaction_focus: "réactions",
  improve_current_team: "améliorer l'équipe actuelle",
  data_quality: "qualité des données",
};

/** Un build est « complet pour le calcul » si aucun champ essentiel ne manque (hors stats finales). */
function buildGaps(b: PlayerCharacterBuild): string[] {
  const gaps: string[] = [];
  if (b.level === undefined) gaps.push("niveau");
  if (!b.weapon) gaps.push("arme");
  if (!b.artifactSlots || b.artifactSlots.length < 5) gaps.push("artéfacts (< 5 pièces scannées)");
  if (!b.talents) gaps.push("talents");
  return gaps;
}

export function buildRecommendations(
  request: RecommendationRequest,
  ownedBuilds: PlayerCharacterBuild[],
  teams: TeamForReco[],
  provenance: { source?: string; importedAt?: string } | null,
): RecommendationResult {
  const excluded = new Set(request.constraints?.excludedCharacterIds ?? []);
  const owned = new Map(ownedBuilds.map((b) => [b.characterId, b] as const));

  // 1) Éliminer l'invalide : ne recommander que des personnages POSSÉDÉS et non exclus.
  const candidates = ownedBuilds.filter((b) => !excluded.has(b.characterId));
  // Ensemble autorisé, appliqué à TOUTES les branches (audit Codex Medium #1) : un personnage
  // exclu ou non possédé ne doit JAMAIS ressortir en recommandation ni en goulot d'étranglement.
  const allowed = new Set(candidates.map((b) => b.characterId));

  const recommendations: RecommendationItem[] = [];
  const missingData: string[] = [];

  if (candidates.length === 0) {
    missingData.push("Aucun personnage possédé exploitable (scan vide ou tous exclus).");
  }

  // 2/3) Recommandations prouvables selon l'objectif.
  if (request.objective === "data_quality" || request.objective === "improve_current_team") {
    // Personnages possédés au build incomplet → recommandation d'amélioration (evidence = gaps réels).
    const incomplete = candidates
      .map((b) => ({ b, gaps: buildGaps(b) }))
      .filter((x) => x.gaps.length > 0)
      .sort((a, b) => b.gaps.length - a.gaps.length)
      .slice(0, 6);
    for (const { b, gaps } of incomplete) {
      recommendations.push({
        type: gaps.includes("arme") ? "weapon" : gaps.includes("talents") ? "talent" : "character_upgrade",
        title: `Compléter le build de ${b.characterId}`,
        explanation: `Le scan du compte montre des données manquantes pour ${b.characterId}, ce qui empêche un calcul de dégâts fiable.`,
        evidence: [
          `Niveau : ${b.level ?? "inconnu"}`,
          `Manque : ${gaps.join(", ")}`,
          ...(b.weapon ? [`Arme : ${b.weapon.id}${b.weapon.refinement ? ` R${b.weapon.refinement}` : ""}`] : []),
        ],
        tradeoffs: ["Investissement en ressources (mora, matériaux, artéfacts) requis."],
        expectedImpact: "améliore la fiabilité du calcul",
        confidence: "high",
        requiredData: gaps,
      });
    }
    if (incomplete.length === 0) {
      recommendations.push({
        type: "data_quality",
        title: "Aucune donnée manquante détectée",
        explanation: "Tous les personnages possédés analysés ont un build scanné suffisant pour le calcul.",
        evidence: [`${candidates.length} personnages possédés analysés.`],
        tradeoffs: [],
        expectedImpact: "non quantifié",
        confidence: "high",
        requiredData: [],
      });
    }
  }

  if (request.objective === "improve_current_team" && request.currentTeamId) {
    const team = teams.find((t) => t.id === request.currentTeamId);
    if (!team) {
      missingData.push("Équipe actuelle introuvable.");
    } else {
      // Membres non évaluables (exclus ou absents du scan) → signalés, jamais présentés comme
      // un « goulot améliorable » (on ne peut pas améliorer un perso non possédé/exclu).
      const notAvailable = team.members.filter((m) => !allowed.has(m));
      for (const m of notAvailable) {
        missingData.push(`Membre « ${m} » exclu ou absent du scan — non évaluable pour l'amélioration.`);
      }
      // Identifier le membre AUTORISÉ le plus limitant (build le plus incomplet).
      const scored = team.members
        .filter((m) => allowed.has(m))
        .map((name) => ({ name, gaps: buildGaps(owned.get(name)!) }));
      const bottleneck = scored.filter((s) => s.gaps.length > 0).sort((a, b) => b.gaps.length - a.gaps.length)[0];
      if (bottleneck) {
        recommendations.unshift({
          type: "character_upgrade",
          title: `Goulot d'étranglement de « ${team.name} » : ${bottleneck.name}`,
          explanation: `Dans cette équipe, ${bottleneck.name} a le build le moins complet — c'est le membre qui limite le plus un calcul de rotation fiable.`,
          evidence: [`Manque : ${bottleneck.gaps.join(", ")}`],
          tradeoffs: ["Prioriser ce personnage peut retarder d'autres améliorations."],
          expectedImpact: "améliore la fiabilité du calcul",
          confidence: "high",
          requiredData: bottleneck.gaps,
        });
      } else if (scored.length > 0) {
        recommendations.unshift({
          type: "rotation",
          title: `« ${team.name} » : builds complets`,
          explanation: "Tous les membres ont un build scanné suffisant ; définis une rotation dans /rotations pour un DPS chiffré.",
          evidence: [`${team.members.length} membres, tous scannés.`],
          tradeoffs: [],
          expectedImpact: "non quantifié",
          confidence: "high",
          requiredData: [],
        });
      }
    }
  }

  if (request.objective === "highest_complete_dps") {
    // Équipes dont TOUS les membres ont un build complet → candidates à un DPS fiable.
    const ranked = teams
      .map((t) => {
        // Audit Codex Medium #1 : seuls les membres AUTORISÉS (possédés, non exclus) comptent.
        const complete = t.members.filter((m) => allowed.has(m) && buildGaps(owned.get(m)!).length === 0).length;
        return { t, complete, total: t.members.length };
      })
      .filter((x) => x.total > 0)
      .sort((a, b) => b.complete / b.total - a.complete / a.total);
    for (const { t, complete, total } of ranked.slice(0, 5)) {
      recommendations.push({
        type: "team",
        title: `${t.name} — ${complete}/${total} membres au build complet`,
        explanation:
          complete === total
            ? "Tous les membres ont un build scanné complet : cette équipe peut produire un DPS fiable via /rotations."
            : "Build partiellement complet : le DPS ne sera fiable qu'après complétion des membres manquants.",
        evidence: [`${complete}/${total} membres avec build complet (niveau + arme + 5 artéfacts + talents).`],
        tradeoffs: complete === total ? [] : ["Nécessite d'améliorer les membres incomplets pour un chiffre fiable."],
        expectedImpact: "non quantifié",
        confidence: complete === total ? "high" : "medium",
        requiredData: complete === total ? [] : ["builds complets des membres manquants"],
      });
    }
    if (ranked.length === 0) missingData.push("Aucune équipe sauvegardée à évaluer.");
  }

  // Objectifs non encore pris en charge quantitativement : honnêteté explicite.
  if (["balanced_team", "low_investment", "survivability", "reaction_focus"].includes(request.objective)) {
    recommendations.push({
      type: "data_quality",
      title: `Objectif « ${OBJECTIVE_LABELS[request.objective]} » : recommandation qualitative uniquement`,
      explanation:
        "Cet objectif exige des critères (soin, bouclier, énergie, uptime de réaction) non encore modélisés par le moteur déterministe. Aucune recommandation chiffrée n'est fournie pour éviter un faux résultat.",
      evidence: [`${candidates.length} personnages possédés disponibles.`],
      tradeoffs: [],
      expectedImpact: "non quantifié",
      confidence: "low",
      requiredData: ["modélisation soin/bouclier/énergie (tranche future)"],
    });
    missingData.push(`Critères de l'objectif « ${OBJECTIVE_LABELS[request.objective]} » non encore modélisés.`);
  }

  const confidence: "high" | "medium" | "low" =
    recommendations.length === 0
      ? "low"
      : recommendations.every((r) => r.confidence === "high")
        ? "high"
        : recommendations.some((r) => r.confidence === "high")
          ? "medium"
          : "low";

  return {
    contractVersion: RECOMMENDATIONS_CONTRACT_VERSION,
    objective: request.objective,
    recommendations,
    assumptions: [
      "Recommandations fondées uniquement sur les données réelles du scan du compte et les équipes sauvegardées.",
      "Aucun personnage non possédé n'est recommandé ; les exclusions sont respectées.",
      "Aucun impact chiffré n'est inventé : l'impact est qualitatif tant que le moteur ne peut pas le prouver.",
    ],
    provenance: provenance ? [{ source: provenance.source ?? "scan local", importedAt: provenance.importedAt }] : [],
    missingData,
    confidence,
  };
}
