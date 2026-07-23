"""Dispatcher CANONIQUE du moteur — l'UNIQUE table de méthodes, partagée par :
- `scripts/engine_stdio.py` (pont web, spawné par SidecarEngineClient),
- `src/irminsul/sidecar.py` (point d'entrée du binaire PyInstaller),
- `account_ipc.dispatch` (ré-export de compatibilité CLI/tests).

Plus jamais deux listes de méthodes maintenues à la main : la découverte
(`engine_capabilities`) et la provenance (`engine_provenance`) sont DÉRIVÉES de la table.
"""
from __future__ import annotations

import hashlib
import sys
from typing import Any, Callable

IPC_CONTRACT_VERSION = "engine-ipc/1.0"
CONTRACTS = {
    "direct_hit": "direct_hit@irminsul-damage",
    "reactions": "reactions/1.0",
    "final_stats": "final-stats/1.0",
    "rotation": "rotation/1.0",
    "export": "irminsul-export/1.0",
}


# --------------------------------------------------------------------------- #
# Méthodes compte (délégation aux payloads existants — imports paresseux).
# --------------------------------------------------------------------------- #
def _profile(_p: dict[str, Any]) -> dict[str, Any]:
    from .account_ipc import profile_payload
    return profile_payload()


def _overview(_p: dict[str, Any]) -> dict[str, Any]:
    from .account_ipc import overview_payload
    return overview_payload()


def _roster(_p: dict[str, Any]) -> dict[str, Any]:
    from .account_ipc import roster_payload
    return roster_payload()


def _import_good(p: dict[str, Any]) -> dict[str, Any]:
    from .account_ipc import import_payload
    path = p.get("path")
    if not path:
        raise ValueError("paramètre 'path' requis")
    return import_payload(str(path))


def _mechanics(_p: dict[str, Any]) -> dict[str, Any]:
    from .quickcalc import mechanics_payload
    return mechanics_payload()


def _quick_calc(p: dict[str, Any]) -> dict[str, Any]:
    from .quickcalc import quickcalc_payload
    return quickcalc_payload(p)


def _characters(_p: dict[str, Any]) -> dict[str, Any]:
    from .charstats import characters_payload
    return characters_payload()


def _character_stats(p: dict[str, Any]) -> dict[str, Any]:
    from .charstats import character_payload
    key = p.get("key")
    if not key:
        raise ValueError("paramètre 'key' requis")
    return character_payload(str(key))


# --------------------------------------------------------------------------- #
# Méthodes calcul (moteur vérifié : damage/reaction/charstats/rotation).
# --------------------------------------------------------------------------- #
def _direct_hit(p: dict[str, Any]) -> dict[str, Any]:
    from .damage import calculate_direct_hit
    return calculate_direct_hit(**p).to_dict()


def _amplifying(p: dict[str, Any]) -> dict[str, Any]:
    from .reaction import amplifying_multiplier
    return amplifying_multiplier(**p).to_dict()


def _transformative(p: dict[str, Any]) -> dict[str, Any]:
    from .reaction import transformative_reaction
    return transformative_reaction(**p).to_dict()


def _lunar_charged(p: dict[str, Any]) -> dict[str, Any]:
    from .reaction import lunar_charged_reaction
    return lunar_charged_reaction(**p).to_dict()


def _lunar(p: dict[str, Any]) -> dict[str, Any]:
    from .reaction import lunar_reaction
    return lunar_reaction(**p).to_dict()


def _additive(p: dict[str, Any]) -> dict[str, Any]:
    from .reaction import additive_reaction
    return additive_reaction(**p).to_dict()


def _run_gcsim(p: dict[str, Any]) -> dict[str, Any]:
    from .gcsim import run_gcsim_content
    return run_gcsim_content(str(p.get("config", "")))


def _final_stats(p: dict[str, Any]) -> dict[str, Any]:
    key = p.get("key")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("paramètre 'key' (nom du personnage) requis")
    from .charstats import character_payload
    return character_payload(key.strip())


def _rotation(p: dict[str, Any]) -> dict[str, Any]:
    from .rotation import calculate_rotation
    team, actions = p.get("team"), p.get("actions")
    if not isinstance(team, list):
        raise ValueError("paramètre 'team' (liste) requis")
    if not isinstance(actions, list):
        raise ValueError("paramètre 'actions' (liste) requis")
    return calculate_rotation(team, actions, p.get("enemy") or {})


# --------------------------------------------------------------------------- #
# Provenance / capabilities — DÉRIVÉES de la table (jamais une liste à la main).
# --------------------------------------------------------------------------- #
def _buildinfo() -> dict[str, Any]:
    """Infos figées au build (générées par scripts/build_sidecar.py) ; fallback dev = git live.

    Audit L5 : `_buildinfo` n'est consulté QUE gelé — en mode source, un artefact de build
    résiduel ne peut pas maquiller la provenance (le git live fait foi).
    """
    if getattr(sys, "frozen", False):
        try:
            from . import _buildinfo as bi  # type: ignore[attr-defined]
            return {"git_commit": bi.GIT_COMMIT, "built_at": bi.BUILT_AT, "build_python": bi.PYTHON}
        except Exception:  # noqa: BLE001 — binaire sans buildinfo : dégradé explicite
            return {"git_commit": None, "built_at": None, "build_python": None}
    if True:  # mode source : git live uniquement
        try:
            import subprocess
            commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, timeout=3, check=False,
            ).stdout.strip() or None
        except Exception:  # noqa: BLE001
            commit = None
        return {"git_commit": commit, "built_at": None, "build_python": None}


def _binary_sha256() -> str | None:
    """SHA-256 du binaire gelé (identité vérifiable) ; None en exécution source."""
    if not getattr(sys, "frozen", False):
        return None
    try:
        h = hashlib.sha256()
        with open(sys.executable, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:  # noqa: BLE001
        return None


def engine_provenance(_p: dict[str, Any] | None = None) -> dict[str, Any]:
    info = _buildinfo()
    return {
        "engine": "python-sidecar",
        "ipc_contract": IPC_CONTRACT_VERSION,
        "contracts": CONTRACTS,
        "methods": sorted(CANONICAL_METHODS.keys()),
        "frozen_binary": bool(getattr(sys, "frozen", False)),
        "python": sys.version.split()[0],
        "binary_sha256": _binary_sha256(),
        **info,
    }


def _capabilities(_p: dict[str, Any]) -> dict[str, Any]:
    return {"ipc_contract": IPC_CONTRACT_VERSION, "methods": sorted(CANONICAL_METHODS.keys())}


CANONICAL_METHODS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    # Compte (noms historiques kebab conservés — compat CLI/binaire existants)
    "profile": _profile,
    "overview": _overview,
    "roster": _roster,
    "import-good": _import_good,
    "mechanics": _mechanics,
    "quick-calc": _quick_calc,
    "characters": _characters,
    "character-stats": _character_stats,
    # Calculs (noms snake conservés — compat SidecarEngineClient web)
    "calculate_direct_hit": _direct_hit,
    "amplifying_multiplier": _amplifying,
    "transformative_reaction": _transformative,
    "lunar_charged_reaction": _lunar_charged,
    "lunar_reaction": _lunar,
    "additive_reaction": _additive,
    "run_gcsim": _run_gcsim,
    "character_final_stats": _final_stats,
    "calculate_rotation": _rotation,
    # Découverte / provenance (dérivées)
    "engine_provenance": lambda p: engine_provenance(p),
    "engine_capabilities": _capabilities,
}


def dispatch(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Point d'entrée canonique : source ET binaire gelé passent par ICI."""
    fn = CANONICAL_METHODS.get(method)
    if fn is None:
        raise ValueError(f"méthode inconnue: {method}")
    p = params or {}
    if not isinstance(p, dict):
        raise ValueError("params doit être un objet")
    return fn(p)
