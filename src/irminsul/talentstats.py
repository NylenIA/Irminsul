"""Multiplicateurs de talents par niveau (1..15), étiquetés et sourcés.

Principe d'honnêteté : genshin-db fournit les tables de valeurs (`stats/talents.json`,
`combat1/2/3` = Attaque Normale / Compétence / Déchaînement, `paramN[niveau-1]`) et les
**libellés** localisés (`English/talents/<perso>.json`, `attributes.labels` au format
`"Libellé|{paramX:format}"`). On joint les deux pour exposer chaque attribut AVEC son
libellé EXACT du jeu et sa/ses valeur(s) par niveau. On **n'auto-décide pas** quel attribut
est « le » multiplicateur : l'utilisateur choisit par libellé → zéro mauvaise attribution.

Le format indique la nature : `…P` (F1P/F2P/P) = pourcentage/multiplicateur (la valeur
stockée EST le multiplicateur décimal) ; `F1/F2/I` = valeur brute (endurance, durée,
énergie… — PAS un multiplicateur). On marque `is_percent` et un indice `is_damage`.

Voyageur : les talents DIFFÈRENT selon l'élément → pas de collapse vers aether (contrairement
aux stats de base). Normalisation = minuscule alphanumérique simple.
"""

from __future__ import annotations

import json
import math
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from .paths import project_root

SLOTS = {"combat1": "normal", "combat2": "skill", "combat3": "burst"}
MIN_TALENT_LEVEL = 1
MAX_TALENT_LEVEL = 15

_LABEL_RE = re.compile(r"^(.*?)\|(.+)$")
_PARAM_RE = re.compile(r"\{(param\d+):([A-Za-z0-9]+)\}")

FORMULA_SOURCES = [
    {"name": "genshin-db (theBowja) — talent data + labels", "type": "B",
     "url": "https://github.com/theBowja/genshin-db"},
    {"name": "KQM — Talent scaling (multiplicateurs par niveau)", "type": "B",
     "url": "https://library.keqingmains.com/"},
]


class UnsupportedTalentError(ValueError):
    """Perso/talent absent de la source locale → non pris en charge (jamais inventé)."""


def normalize_key(good_key: str) -> str:
    """Clé GOOD perso → clé genshin-db (minuscule, alphanum). Voyageur conservé par
    élément (ex. TravelerElectro → travelerelectro), car ses talents en dépendent."""
    return re.sub(r"[^a-z0-9]", "", str(good_key).lower())


_REL = Path("data") / "mechanics" / "talent-multipliers.json"


def _candidate_roots() -> list[Path]:
    roots: list[Path] = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        roots.append(Path(sys._MEIPASS))  # type: ignore[attr-defined]
    roots.append(Path(__file__).resolve().parents[2])
    roots.append(project_root())
    return roots


def data_path() -> Path:
    for root in _candidate_roots():
        candidate = root / _REL
        if candidate.exists():
            return candidate
    return _candidate_roots()[0] / _REL


@lru_cache(maxsize=1)
def _load_cached(path_str: str, mtime: float) -> dict[str, Any]:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def load_talents() -> dict[str, Any]:
    p = data_path()
    if not p.exists():
        raise FileNotFoundError(
            f"Données de talents absentes : {p}. "
            "Régénérer via `python tools/extract_talent_multipliers.py`."
        )
    return _load_cached(str(p), p.stat().st_mtime)


def supported_characters() -> set[str]:
    return set(load_talents().get("characters", {}).keys())


def _slot_key(slot: str) -> str:
    """Accepte 'combat1'/'normal'/'na'/'skill'/'burst' → clé interne combatN."""
    s = str(slot).strip().lower()
    alias = {"normal": "combat1", "na": "combat1", "auto": "combat1",
             "skill": "combat2", "e": "combat2",
             "burst": "combat3", "q": "combat3"}
    if s in SLOTS:
        return s
    if s in alias:
        return alias[s]
    raise ValueError(f"talent inconnu: {slot!r} (attendu combat1/2/3 ou normal/skill/burst)")


def talent_attributes(char_key: str, slot: str, level: int) -> dict[str, Any]:
    """Attributs étiquetés d'un talent à un niveau donné, avec leur valeur résolue.

    Renvoie ``{"supported": True, "slot", "role", "attributes": [...]}`` ou
    ``{"supported": False, "reason": ...}``. Aucune valeur inventée."""
    level = int(level)
    if not (MIN_TALENT_LEVEL <= level <= MAX_TALENT_LEVEL):
        return {"supported": False, "reason": f"niveau de talent hors bornes (1..15): {level}"}
    try:
        ck = normalize_key(char_key)
        sk = _slot_key(slot)
    except ValueError as exc:
        return {"supported": False, "reason": str(exc)}
    data = load_talents()
    char = data.get("characters", {}).get(ck)
    if char is None:
        return {"supported": False, "reason": f"talents non pris en charge: {char_key!r} ({ck!r})"}
    sd = char.get(sk)
    if not sd:
        return {"supported": False, "reason": f"talent {sk} absent pour {char_key!r}"}

    out_attrs: list[dict[str, Any]] = []
    for attr in sd["attributes"]:
        per_level = attr["values"][level - 1]
        if per_level is not None and not math.isfinite(per_level):
            per_level = None  # jamais de NaN/inf en sortie
        out_attrs.append({
            "label": attr["label"],
            "params": attr["params"],
            "is_percent": attr["is_percent"],
            "is_damage": attr["is_damage"],
            "value": per_level,
        })
    return {"supported": True, "slot": sk, "role": SLOTS[sk],
            "name": sd.get("name"), "level": level, "attributes": out_attrs,
            "provenance": data.get("provenance", {})}


def talent_multiplier(char_key: str, slot: str, label: str, level: int) -> dict[str, Any]:
    """Valeur d'un attribut de talent précis (par libellé EXACT). Erreur explicite sinon."""
    res = talent_attributes(char_key, slot, level)
    if not res.get("supported"):
        return res
    for a in res["attributes"]:
        if a["label"] == label:
            return {"supported": True, "label": label, "value": a["value"],
                    "is_percent": a["is_percent"], "is_damage": a["is_damage"],
                    "slot": res["slot"], "role": res["role"], "level": level,
                    "provenance": res["provenance"]}
    avail = [a["label"] for a in res["attributes"]]
    return {"supported": False, "reason": f"libellé inconnu {label!r}", "available": avail}


# --------------------------------------------------------------------------- #
# Extraction (pure) — utilisée par tools/extract_talent_multipliers.py.
# --------------------------------------------------------------------------- #
_DMG_RE = re.compile(r"\bDMG\b")


def _is_damage(label: str, is_percent: bool) -> bool:
    """Indice (non autoritatif) : multiplicateur de DÉGÂTS plutôt que buff/valeur annexe.
    L'utilisateur voit le libellé exact ; ce drapeau ne sert qu'au filtrage par défaut."""
    if not is_percent:
        return False
    if not _DMG_RE.search(label):
        return False
    low = label.lower()
    return not any(w in low for w in ("bonus", "increase", "regeneration", "res ", "reduction"))


def _resolve_values(params: list[str], op_plus: bool, stat_slot: dict[str, Any]) -> list[float | None]:
    """Valeur par niveau (1..15) : somme des params si expression additive, sinon 1er param."""
    arrays = [stat_slot.get(p) for p in params]
    out: list[float | None] = []
    for i in range(MAX_TALENT_LEVEL):
        vals = [arr[i] for arr in arrays if arr and i < len(arr)]
        if not vals:
            out.append(None)
        elif op_plus:
            out.append(round(sum(vals), 6))
        else:
            out.append(round(vals[0], 6))
    return out


def extract_talents_from_genshin_db(source_root: Path, provenance: dict[str, Any]) -> dict[str, Any]:
    sd = source_root / "src" / "data"
    stats = json.loads((sd / "stats" / "talents.json").read_text(encoding="utf-8"))
    en_dir = sd / "English" / "talents"

    characters: dict[str, Any] = {}
    skipped: list[str] = []
    for ckey, cstats in stats.items():
        en_file = en_dir / f"{ckey}.json"
        if not en_file.exists():
            skipped.append(ckey)
            continue
        en = json.loads(en_file.read_text(encoding="utf-8"))
        char_out: dict[str, Any] = {}
        for slot in SLOTS:
            labels = (en.get(slot, {}) or {}).get("attributes", {}).get("labels", [])
            stat_slot = cstats.get(slot, {})
            attrs: list[dict[str, Any]] = []
            for lab in labels:
                m = _LABEL_RE.match(lab)
                if not m:
                    continue
                name, expr = m.group(1).strip(), m.group(2)
                found = _PARAM_RE.findall(expr)
                if not found:
                    continue
                params = [p for p, _ in found]
                fmts = [f for _, f in found]
                is_percent = any("P" in f for f in fmts)
                op_plus = "+" in expr and len(params) > 1
                values = _resolve_values(params, op_plus, stat_slot)
                if all(v is None for v in values):
                    continue
                attrs.append({
                    "label": name, "expr": expr, "params": params,
                    "is_percent": is_percent, "is_damage": _is_damage(name, is_percent),
                    "values": values,
                })
            if attrs:
                char_out[slot] = {"name": (en.get(slot, {}) or {}).get("name"),
                                  "attributes": attrs}
        if char_out:
            characters[ckey] = char_out
        else:
            skipped.append(ckey)

    prov = dict(provenance)
    prov.setdefault("formula", "multiplicateur = stats/talents.json combatN.paramX[niveau-1] ; "
                               "libellés depuis English/talents (attributes.labels)")
    prov.setdefault("formula_sources", FORMULA_SOURCES)
    prov["character_count"] = len(characters)
    prov["skipped_count"] = len(skipped)
    return {
        "schema": 1,
        "kind": "talent-multipliers",
        "version": prov.get("source_commit_date", prov.get("extracted_at", "")),
        "provenance": prov,
        "characters": dict(sorted(characters.items())),
    }
