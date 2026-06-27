"""Logique vérifiable de la politique de recherche/rigueur (docs/RESEARCH_POLICY.md).

Ces fonctions sont **pures et testées** : elles donnent au projet des garde-fous
exécutables (et non seulement des consignes en prose) — déclenchement de recherche,
fraîcheur, hiérarchie/qualité des sources, contradictions, bannière de leak, sûreté
d'un skill externe, et gestion explicite de l'inconnu (pas d'invention).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

# --------------------------------------------------------------------------- #
# 1. Déclenchement de recherche
# --------------------------------------------------------------------------- #
# Sujets intrinsèquement volatils / liés à une version → recherche obligatoire.
RESEARCH_TRIGGERS: tuple[str, ...] = (
    "meta", "méta", "patch", "version", "banner", "bannière", "tier", "best team",
    "meilleure team", "meilleure équipe", "leak", "leaks", "rumeur", "rumor",
    "beta", "bêta", "release", "sortie", "rerun", "abyss", "abîme", "event",
    "événement", "buff", "nerf", "changelog", "api", "library", "bibliothèque",
    "dependency", "dépendance", "latest", "actuel", "current", "aujourd", "prix",
    "kit", "scaling", "multiplicateur", "constellation", "weapon banner",
)

# Faits stables, vérifiables localement → pas besoin de re-rechercher.
STABLE_TOPICS: tuple[str, ...] = (
    "formule de dégâts", "damage formula", "résistance", "resistance formula",
    "defense formula", "formule de défense", "ascension levels", "max level 90",
)


@dataclass(slots=True)
class ResearchDecision:
    required: bool
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"required": self.required, "reasons": self.reasons}


def requires_research(
    topic: str, *, locally_verifiable: bool = False, certain: bool = False,
) -> ResearchDecision:
    """Décide si un sujet exige une recherche avant de répondre/agir.

    Règle : tout sujet volatil/versionné/incertain/leak → recherche. Un fait stable,
    vérifiable localement ET certain → pas de recherche (ne pas bloquer inutilement).
    """
    text = (topic or "").lower()
    reasons: list[str] = []
    for kw in RESEARCH_TRIGGERS:
        if kw in text:
            reasons.append(f"sujet volatil/versionné détecté : '{kw}'")
            break
    if not certain:
        reasons.append("certitude non garantie")
    if locally_verifiable and certain and any(s in text for s in STABLE_TOPICS):
        # Fait stable et vérifiable → on retire l'exigence.
        return ResearchDecision(required=False, reasons=["fait stable vérifiable localement"])
    required = bool(reasons)
    return ResearchDecision(required=required, reasons=reasons or ["aucun déclencheur"])


# --------------------------------------------------------------------------- #
# 2. Fraîcheur / obsolescence
# --------------------------------------------------------------------------- #
def is_stale(indexed_at_iso: str | None, *, max_hours: float = 24.0, now: datetime | None = None) -> bool:
    """Vrai si la donnée locale est trop ancienne (ou absente de date)."""
    if not indexed_at_iso:
        return True
    try:
        indexed = datetime.fromisoformat(indexed_at_iso)
    except ValueError:
        return True
    if indexed.tzinfo is None:
        indexed = indexed.replace(tzinfo=UTC)
    now = now or datetime.now(UTC)
    return (now - indexed).total_seconds() / 3600.0 > max_hours


# --------------------------------------------------------------------------- #
# 3. Sources : qualité, primaire/repost, contradictions
# --------------------------------------------------------------------------- #
_TIER_RANK = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}


@dataclass(slots=True)
class SourceRef:
    name: str
    tier: str = "C"
    date: str | None = None        # ISO ; None = sans date (pénalisé)
    url: str | None = None
    is_primary: bool = False
    is_repost: bool = False
    claimed_primary: bool = False  # se présente comme primaire


def source_quality(ref: SourceRef) -> dict[str, object]:
    """Note la fiabilité d'une source et liste ses problèmes (issues)."""
    issues: list[str] = []
    penalty = 0.0
    if ref.date is None:
        issues.append("source sans date — fiabilité réduite")
        penalty += 0.30
    if ref.is_repost:
        issues.append("repost — préférer la source d'origine")
        penalty += 0.25
    if ref.claimed_primary and not ref.is_primary:
        issues.append("source secondaire présentée comme primaire")
        penalty += 0.35
    base = 1.0 - _TIER_RANK.get(ref.tier.upper(), 3) * 0.18
    reliability = max(0.0, round(base * (1 - penalty), 3))
    return {"name": ref.name, "reliability": reliability, "tier": ref.tier.upper(),
            "issues": issues}


def more_reliable(a: SourceRef, b: SourceRef) -> SourceRef:
    """Renvoie la source la plus fiable (un original prime sur son repost)."""
    qa = source_quality(a)["reliability"]
    qb = source_quality(b)["reliability"]
    return a if qa >= qb else b  # type: ignore[return-value]


def detect_contradictions(claims: list[dict[str, object]]) -> list[dict[str, object]]:
    """Repère des affirmations contradictoires : même 'key', 'value' différentes.

    claims : [{"source": str, "key": str, "value": Any, "date": iso|None}, ...]
    """
    by_key: dict[object, list[dict[str, object]]] = {}
    for c in claims:
        by_key.setdefault(c.get("key"), []).append(c)
    out: list[dict[str, object]] = []
    for key, group in by_key.items():
        values = {c.get("value") for c in group}
        if len(values) > 1:
            out.append({
                "key": key,
                "values": sorted(map(str, values)),
                "sources": [c.get("source") for c in group],
                "note": "Contradiction entre sources : vérifier dates et versions, ne pas trancher au hasard.",
            })
    return out


# --------------------------------------------------------------------------- #
# 4. Leaks : bannière toujours présente, jamais "officiel"
# --------------------------------------------------------------------------- #
LEAK_BANNER = (
    "⚠️ LEAK NON CONFIRMÉ — ces informations peuvent changer, être incomplètes ou être fausses."
)
_FORBIDDEN_LEAK_WORDS = ("officiel", "confirmé", "définitif", "garanti", "official", "confirmed")


def format_leak(
    body: str, *, leak_date: str | None, supposed_version: str | None,
    confidence: str, confirmed: str = "—", uncertain: str = "—", may_change: str = "—",
) -> str:
    """Met en forme une info de leak avec bannière + métadonnées obligatoires.

    Garantit que la sortie n'affirme jamais le caractère officiel/confirmé du leak.
    """
    # NB : on évite le mot « confirmé » dans les libellés pour ne pas déclencher
    # `asserts_official` (un leak ne doit jamais se présenter comme confirmé).
    text = (
        f"{LEAK_BANNER}\n"
        f"- Date du leak : {leak_date or 'inconnue'}\n"
        f"- Version supposée : {supposed_version or 'inconnue'}\n"
        f"- Niveau de confiance : {confidence}\n"
        f"- Éléments corroborés : {confirmed}\n"
        f"- Éléments incertains : {uncertain}\n"
        f"- Ce qui peut encore changer : {may_change}\n\n"
        f"{body}"
    )
    return text


def asserts_official(text: str) -> bool:
    """Vrai si un texte affirme à tort qu'un leak est officiel/confirmé/définitif."""
    low = text.lower()
    if LEAK_BANNER.lower() in low:
        # La bannière elle-même contient "confirmé" (NON CONFIRMÉ) → on l'ignore.
        low = low.replace(LEAK_BANNER.lower(), "")
    return any(w in low for w in _FORBIDDEN_LEAK_WORDS)


# --------------------------------------------------------------------------- #
# 5. Confiance explicite
# --------------------------------------------------------------------------- #
class Confidence(StrEnum):
    HIGH = "Confiance élevée"
    MEDIUM = "Confiance moyenne"
    LOW = "Confiance faible"
    UNVERIFIABLE = "Non vérifiable actuellement"


def assess_confidence(
    *, primary_sources: int = 0, secondary_sources: int = 0, is_leak: bool = False,
    is_beta: bool = False, stale: bool = False, conflicting: bool = False,
    source_found: bool = True,
) -> dict[str, str]:
    """Niveau de confiance cohérent avec les preuves, avec justification courte."""
    if not source_found:
        return {"level": Confidence.UNVERIFIABLE, "why": "source d'origine introuvable"}
    if conflicting:
        return {"level": Confidence.UNVERIFIABLE, "why": "conflit non résolu entre sources fiables"}
    if is_leak or is_beta:
        return {"level": Confidence.LOW, "why": "données de bêta/leak susceptibles de changer"}
    if primary_sources >= 2 and not stale:
        return {"level": Confidence.HIGH, "why": "plusieurs sources primaires concordent"}
    if primary_sources >= 1 or secondary_sources >= 2:
        why = "recoupement partiel" + (" mais données anciennes" if stale else "")
        return {"level": Confidence.MEDIUM, "why": why}
    if secondary_sources == 1:
        return {"level": Confidence.LOW, "why": "une seule source secondaire"}
    return {"level": Confidence.UNVERIFIABLE, "why": "aucune source fiable trouvée"}


# --------------------------------------------------------------------------- #
# 6. Inconnu : marquer, ne pas inventer
# --------------------------------------------------------------------------- #
def safe_unknown(field_name: str, *, action: str = "rechercher une source primaire") -> dict[str, object]:
    """Représentation explicite d'une valeur inconnue (jamais inventée)."""
    return {
        "field": field_name,
        "value": None,
        "status": "unverified",
        "confidence": str(Confidence.UNVERIFIABLE),
        "action": action,
    }


# --------------------------------------------------------------------------- #
# 7. Sûreté d'un skill externe (find-skills / skills.sh)
# --------------------------------------------------------------------------- #
_SUSPICIOUS_PERMS = ("network", "exfiltrate", "upload", "credentials", "secret",
                     "token", "shell:*", "rm -rf", "curl http", "wget http")


def evaluate_external_skill(manifest: dict[str, object]) -> dict[str, object]:
    """Décision sûre/à refuser pour un skill externe, avant toute installation.

    manifest : {"name", "author", "permissions": [...], "commands": [...],
                "dependencies": [...], "sends_personal_data": bool, "url"}
    """
    reasons: list[str] = []
    perms = [str(p).lower() for p in (manifest.get("permissions") or [])]
    cmds = " ".join(str(c).lower() for c in (manifest.get("commands") or []))
    blob = " ".join(perms) + " " + cmds
    for token in _SUSPICIOUS_PERMS:
        if token in blob:
            reasons.append(f"permission/commande suspecte : '{token}'")
    if manifest.get("sends_personal_data"):
        reasons.append("envoie des données personnelles")
    if not manifest.get("author"):
        reasons.append("auteur inconnu / non vérifié")
    if not manifest.get("url"):
        reasons.append("dépôt source absent (inspection impossible)")
    allow = not reasons
    return {
        "name": manifest.get("name", "?"),
        "allow": allow,
        "reasons": reasons or ["aucun signal suspect — inspection manuelle toujours requise"],
        "note": "Ne jamais installer en boîte noire ni par popularité ; préférer un skill local si doute.",
    }
