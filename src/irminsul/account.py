"""Import, validation et normalisation d'un export de compte Genshin au format GOOD.

Pensé pour les exports Inventory Kamera (GOOD v3) mais tolérant aux autres
producteurs GOOD. Principes :

* le fichier brut n'est JAMAIS modifié ni envoyé à un service externe ;
* chaque donnée normalisée garde une `provenance` (tableau + index d'origine) ;
* le champ `id` d'Inventory Kamera n'est pas une clé fiable (plusieurs armes
  1★ partagent `id=0`) → on fabrique des identifiants internes stables ;
* l'import est idempotent : ré-importer le même contenu (même SHA-256) ne
  recrée pas de snapshot.

Niveaux de sévérité des anomalies : INFO < WARNING < ERROR < BLOCKING.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .paths import account_dir, account_subdir, project_root

GOOD_SLOTS = ("flower", "plume", "sands", "goblet", "circlet")
SEVERITIES = ("INFO", "WARNING", "ERROR", "BLOCKING")


# --------------------------------------------------------------------------- #
# Hashing / identifiants stables
# --------------------------------------------------------------------------- #
def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _short_hash(*parts: Any, length: int = 8) -> str:
    raw = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def stable_weapon_id(index: int, weapon: dict[str, Any]) -> str:
    """Identifiant interne stable d'une arme.

    Inclut l'index d'origine pour que deux exemplaires identiques restent
    distincts (on ne fusionne jamais deux armes par nom/niveau/raffinement).
    """
    key = weapon.get("key", "Unknown")
    h = _short_hash(
        "weapon", index, key, weapon.get("level"),
        weapon.get("ascension"), weapon.get("refinement"), weapon.get("location"),
    )
    return f"w-{index:03d}-{key}-r{weapon.get('refinement', '?')}-{h}"


def stable_artifact_id(index: int, artifact: dict[str, Any]) -> str:
    set_key = artifact.get("setKey", "Unknown")
    slot = artifact.get("slotKey", "?")
    h = _short_hash(
        "artifact", index, set_key, slot, artifact.get("mainStatKey"),
        artifact.get("level"), artifact.get("rarity"), artifact.get("location"),
    )
    return f"a-{index:03d}-{set_key}-{slot}-{h}"


# --------------------------------------------------------------------------- #
# Lecture
# --------------------------------------------------------------------------- #
def load_good(path: str | Path) -> dict[str, Any]:
    """Lit et valide qu'il s'agit bien d'un export GOOD. Lève sinon (BLOCKING)."""
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = project_root() / file_path
    if not file_path.exists():
        raise FileNotFoundError(f"Export GOOD introuvable : {file_path}")
    if file_path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("Export GOOD trop volumineux (>100 Mo)")
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != "GOOD":
        raise ValueError("Le fichier n'est pas un export GOOD valide (champ format != 'GOOD')")
    return payload


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
@dataclass
class Issue:
    severity: str
    code: str
    message: str
    location: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "location": self.location,
        }


def _is_int_in(value: Any, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def validate_good(payload: dict[str, Any]) -> dict[str, Any]:
    """Valide un payload GOOD et renvoie issues + comptes + ensembles utiles."""
    issues: list[Issue] = []
    add = lambda s, c, m, loc="": issues.append(Issue(s, c, m, loc))  # noqa: E731

    if payload.get("format") != "GOOD":
        add("BLOCKING", "format", "Champ 'format' absent ou != 'GOOD'.")
    version = payload.get("version")
    if version is None:
        add("WARNING", "version", "Champ 'version' absent.")
    elif version != 3:
        add("INFO", "version", f"Version GOOD = {version} (attendu 3 pour Inventory Kamera).")

    characters = payload.get("characters") or []
    weapons = payload.get("weapons") or []
    artifacts = payload.get("artifacts") or []
    materials = payload.get("materials") or {}

    char_keys: set[str] = set()
    for i, c in enumerate(characters):
        loc = f"characters[{i}]"
        key = c.get("key")
        if not key:
            add("ERROR", "char.key", "Personnage sans 'key'.", loc)
            continue
        char_keys.add(key)
        if not _is_int_in(c.get("level"), 1, 90):
            add("ERROR", "char.level", f"{key}: level invalide ({c.get('level')}).", loc)
        if not _is_int_in(c.get("ascension"), 0, 6):
            add("ERROR", "char.ascension", f"{key}: ascension invalide ({c.get('ascension')}).", loc)
        if not _is_int_in(c.get("constellation"), 0, 6):
            add("ERROR", "char.const", f"{key}: constellation invalide ({c.get('constellation')}).", loc)
        talent = c.get("talent") or {}
        for t in ("auto", "skill", "burst"):
            if not _is_int_in(talent.get(t), 1, 10):
                # >10 possible via constellations dans certains exports → WARNING
                if isinstance(talent.get(t), int) and talent.get(t) > 10:
                    add("WARNING", "char.talent", f"{key}: talent {t}={talent.get(t)} (>10).", loc)
                else:
                    add("ERROR", "char.talent", f"{key}: talent {t} invalide ({talent.get(t)}).", loc)

    # Armes
    id_counter: dict[Any, int] = {}
    for i, w in enumerate(weapons):
        loc = f"weapons[{i}]"
        if not w.get("key"):
            add("ERROR", "weapon.key", "Arme sans 'key'.", loc)
        if not _is_int_in(w.get("level"), 1, 90):
            add("ERROR", "weapon.level", f"{w.get('key')}: level invalide ({w.get('level')}).", loc)
        if not _is_int_in(w.get("refinement"), 1, 5):
            add("ERROR", "weapon.refine", f"{w.get('key')}: raffinement invalide ({w.get('refinement')}).", loc)
        id_counter[w.get("id")] = id_counter.get(w.get("id"), 0) + 1
    dup_ids = {k: v for k, v in id_counter.items() if v > 1}
    if dup_ids:
        add(
            "WARNING", "weapon.id_dup",
            f"Champ 'id' non unique : {sum(dup_ids.values())} armes partagent un id dupliqué "
            f"(ex. id={sorted(dup_ids, key=lambda x: -dup_ids[x])[0]} ×"
            f"{max(dup_ids.values())}). Ids internes stables utilisés à la place.",
        )

    # Artefacts
    for i, a in enumerate(artifacts):
        loc = f"artifacts[{i}]"
        if not a.get("setKey"):
            add("ERROR", "art.set", "Artéfact sans 'setKey'.", loc)
        if a.get("slotKey") not in GOOD_SLOTS:
            add("ERROR", "art.slot", f"slotKey invalide ({a.get('slotKey')}).", loc)
        if not _is_int_in(a.get("rarity"), 1, 5):
            add("ERROR", "art.rarity", f"rareté invalide ({a.get('rarity')}).", loc)
        max_level = {1: 4, 2: 4, 3: 12, 4: 16, 5: 20}.get(a.get("rarity"), 20)
        if not _is_int_in(a.get("level"), 0, max_level):
            add("WARNING", "art.level", f"niveau {a.get('level')} hors plage pour rareté {a.get('rarity')}.", loc)
        if not a.get("mainStatKey"):
            add("ERROR", "art.main", "mainStatKey absent.", loc)
        if not isinstance(a.get("substats"), list):
            add("WARNING", "art.subs", "substats absent ou non liste.", loc)

    # Références équipement -> personnages
    unresolved: dict[str, dict[str, Any]] = {}
    for arr_name, arr in (("weapons", weapons), ("artifacts", artifacts)):
        for i, item in enumerate(arr):
            loc_char = item.get("location")
            if loc_char and loc_char not in char_keys:
                entry = unresolved.setdefault(loc_char, {"weapons": [], "artifacts": []})
                entry[arr_name].append(i)
    for name, refs in unresolved.items():
        nb = len(refs["weapons"]) + len(refs["artifacts"])
        add(
            "WARNING", "equip.unresolved",
            f"location='{name}' référencée par {nb} équipement(s) mais absente de characters[] "
            f"→ conservée dans unresolvedCharacters (scan/saisie manuelle requise).",
        )

    if not isinstance(materials, dict):
        add("ERROR", "materials", "Le champ 'materials' n'est pas un objet.")

    counts_by_sev = {s: sum(1 for x in issues if x.severity == s) for s in SEVERITIES}
    return {
        "issues": [x.to_dict() for x in issues],
        "counts_by_severity": counts_by_sev,
        "totals": {
            "characters": len(characters),
            "weapons": len(weapons),
            "artifacts": len(artifacts),
            "materials": len(materials) if isinstance(materials, dict) else 0,
        },
        "character_keys": sorted(char_keys),
        "unresolved_characters": sorted(unresolved.keys()),
        "duplicate_weapon_ids": {str(k): v for k, v in sorted(dup_ids.items(), key=lambda x: -x[1])},
        "is_blocking": counts_by_sev["BLOCKING"] > 0,
    }


# --------------------------------------------------------------------------- #
# Normalisation
# --------------------------------------------------------------------------- #
def normalize(
    payload: dict[str, Any],
    *,
    source_path: str,
    sha: str,
    snapshot_date: str,
) -> dict[str, dict[str, Any]]:
    """Produit la représentation normalisée (un dict par fichier de sortie)."""
    characters = payload.get("characters") or []
    weapons = payload.get("weapons") or []
    artifacts = payload.get("artifacts") or []
    materials = payload.get("materials") or {}

    char_keys = {c.get("key") for c in characters if c.get("key")}

    # Personnages
    norm_chars: dict[str, Any] = {}
    for i, c in enumerate(characters):
        key = c.get("key")
        if not key:
            continue
        norm_chars[key] = {
            "key": key,
            "level": c.get("level"),
            "ascension": c.get("ascension"),
            "constellation": c.get("constellation"),
            "talents": dict(c.get("talent") or {}),
            "weapon": None,         # rempli via equipment
            "artifacts": {},        # slot -> internal id
            "_provenance": {"array": "characters", "index": i},
        }

    # Armes
    norm_weapons: dict[str, Any] = {}
    for i, w in enumerate(weapons):
        wid = stable_weapon_id(i, w)
        norm_weapons[wid] = {
            "internal_id": wid,
            "key": w.get("key"),
            "level": w.get("level"),
            "ascension": w.get("ascension"),
            "refinement": w.get("refinement"),
            "location": w.get("location") or None,
            "lock": bool(w.get("lock", False)),
            "kamera_id": w.get("id"),
            "_provenance": {"array": "weapons", "index": i, "raw_id": w.get("id")},
        }

    # Artefacts
    norm_artifacts: dict[str, Any] = {}
    for i, a in enumerate(artifacts):
        aid = stable_artifact_id(i, a)
        norm_artifacts[aid] = {
            "internal_id": aid,
            "setKey": a.get("setKey"),
            "slotKey": a.get("slotKey"),
            "rarity": a.get("rarity"),
            "level": a.get("level"),
            "mainStatKey": a.get("mainStatKey"),
            "substats": a.get("substats") or [],
            "location": a.get("location") or None,
            "lock": bool(a.get("lock", False)),
            "kamera_id": a.get("id"),
            "_provenance": {"array": "artifacts", "index": i, "raw_id": a.get("id")},
        }

    # Équipement (références croisées) + unresolved
    unresolved: dict[str, Any] = {}
    equipment: dict[str, Any] = {}

    def bucket(name: str) -> dict[str, Any]:
        return unresolved.setdefault(
            name, {"key": name, "weapons": [], "artifacts": {}, "_note": "Personnage non présent dans characters[] — données de perso (élément, niveau, talents, constellation) NON résolues. Nouveau scan ou saisie manuelle requis."}
        )

    for wid, w in norm_weapons.items():
        loc = w["location"]
        if not loc:
            continue
        if loc in norm_chars:
            norm_chars[loc]["weapon"] = wid
            equipment.setdefault(loc, {"weapon": None, "artifacts": {}})["weapon"] = wid
        else:
            bucket(loc)["weapons"].append(wid)

    for aid, a in norm_artifacts.items():
        loc = a["location"]
        if not loc:
            continue
        if loc in norm_chars:
            norm_chars[loc]["artifacts"][a["slotKey"]] = aid
            equipment.setdefault(loc, {"weapon": None, "artifacts": {}})["artifacts"][a["slotKey"]] = aid
        else:
            bucket(loc)["artifacts"][a["slotKey"]] = aid

    free_artifacts = [aid for aid, a in norm_artifacts.items() if not a["location"]]
    free_weapons = [wid for wid, w in norm_weapons.items() if not w["location"]]

    profile = {
        "snapshot_date": snapshot_date,
        "source_path": source_path,
        "sha256": sha,
        "format": payload.get("format"),
        "good_version": payload.get("version"),
        "kamera_version": payload.get("kamera_version"),
        "source": payload.get("source"),
        "counts": {
            "characters": len(norm_chars),
            "weapons": len(norm_weapons),
            "artifacts": len(norm_artifacts),
            "materials": len(materials) if isinstance(materials, dict) else 0,
            "equipped_weapons": sum(1 for w in norm_weapons.values() if w["location"] in char_keys),
            "equipped_artifacts": sum(1 for a in norm_artifacts.values() if a["location"] in char_keys),
            "free_weapons": len(free_weapons),
            "free_artifacts": len(free_artifacts),
            "unresolved_characters": len(unresolved),
        },
        "character_keys": sorted(norm_chars.keys()),
        "unresolved_character_keys": sorted(unresolved.keys()),
        "provenance_note": "Chaque entrée normalisée conserve _provenance{array,index} vers le fichier brut.",
    }

    return {
        "account-profile": profile,
        "characters": {"characters": norm_chars},
        "weapons": {"weapons": norm_weapons, "free": free_weapons},
        "artifacts": {"artifacts": norm_artifacts, "free": free_artifacts},
        "materials": {"materials": materials},
        "equipment": {"equipment": equipment},
        "unresolved-data": {"unresolvedCharacters": unresolved},
    }


# --------------------------------------------------------------------------- #
# Allocation exclusive (Abîme : aucun objet partagé entre deux équipes)
# --------------------------------------------------------------------------- #
class AllocationConflict(RuntimeError):
    """Tentative d'attribuer le même objet (arme/artéfact/perso) deux fois."""


@dataclass
class ExclusiveAllocator:
    """Garantit qu'une arme / un artéfact / un personnage n'est utilisé qu'une fois."""

    _owner: dict[str, str] = field(default_factory=dict)

    def assign(self, item_id: str, holder: str) -> None:
        existing = self._owner.get(item_id)
        if existing is not None and existing != holder:
            raise AllocationConflict(
                f"'{item_id}' déjà attribué à '{existing}', impossible de le donner à '{holder}'."
            )
        self._owner[item_id] = holder

    def owner(self, item_id: str) -> str | None:
        return self._owner.get(item_id)


# --------------------------------------------------------------------------- #
# Import (copie read-only, idempotence, snapshot, diff)
# --------------------------------------------------------------------------- #
def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_readonly(path: Path) -> None:
    try:
        os.chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    except OSError:
        pass


def _manifest_path() -> Path:
    return account_dir() / "manifest.json"


def _load_manifest() -> dict[str, Any]:
    p = _manifest_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"imports": []}


def import_good(
    src: str | Path,
    *,
    snapshot_date: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Importe un GOOD : copie brute read-only, snapshot daté, normalisation, diff.

    Idempotent : si un import du même SHA-256 existe déjà, on ne recrée pas de
    snapshot (sauf force=True), mais on régénère toujours data/account/current/.
    """
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {src_path}")
    snapshot_date = snapshot_date or date.today().isoformat()

    payload = load_good(src_path)
    sha = sha256_file(src_path)
    sha8 = sha[:8]

    manifest = _load_manifest()
    already = next((m for m in manifest["imports"] if m["sha256"] == sha), None)
    is_new = already is None or force

    # 1) Copie brute read-only dans raw/
    raw_dir = account_subdir("raw")
    raw_copy = raw_dir / src_path.name
    if not raw_copy.exists() or force:
        shutil.copy2(src_path, raw_copy)
        _make_readonly(raw_copy)

    # 2) Validation + normalisation
    validation = validate_good(payload)
    normalized = normalize(
        payload, source_path=str(src_path), sha=sha, snapshot_date=snapshot_date
    )

    # 3) Snapshot daté (idempotent)
    snap_name = f"{snapshot_date}__{sha8}"
    snap_dir = account_subdir("snapshots") / snap_name
    snapshot_created = False
    if not snap_dir.exists() or force:
        snap_dir.mkdir(parents=True, exist_ok=True)
        for name, data in normalized.items():
            _write_json(snap_dir / f"{name}.json", data)
        _write_json(snap_dir / "validation.json", validation)
        snapshot_created = True

    # 4) Diff vs snapshot précédent
    prev = _previous_snapshot(exclude=snap_name)
    diff = diff_snapshots(_load_snapshot(prev), normalized) if prev else None

    # 5) current/ = dernière vérité
    current_dir = account_subdir("current")
    for name, data in normalized.items():
        _write_json(current_dir / f"{name}.json", data)

    # 6) Manifest
    if is_new:
        manifest["imports"].append(
            {
                "sha256": sha,
                "snapshot_date": snapshot_date,
                "snapshot": snap_name,
                "raw_file": raw_copy.name,
                "counts": normalized["account-profile"]["counts"],
            }
        )
        _write_json(_manifest_path(), manifest)

    return {
        "sha256": sha,
        "snapshot": snap_name,
        "snapshot_created": snapshot_created,
        "idempotent_skip": bool(already) and not force,
        "raw_copy": str(raw_copy),
        "validation": validation,
        "counts": normalized["account-profile"]["counts"],
        "diff_against": prev,
        "diff": diff,
    }


def _snapshots_root() -> Path:
    return account_subdir("snapshots")


def _previous_snapshot(*, exclude: str) -> str | None:
    snaps = sorted(p.name for p in _snapshots_root().iterdir() if p.is_dir()) if _snapshots_root().exists() else []
    snaps = [s for s in snaps if s != exclude]
    return snaps[-1] if snaps else None


def _load_snapshot(name: str | None) -> dict[str, Any] | None:
    if not name:
        return None
    snap_dir = _snapshots_root() / name
    if not snap_dir.exists():
        return None
    out: dict[str, Any] = {}
    for f in snap_dir.glob("*.json"):
        out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return out


def diff_snapshots(old: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    """Compare deux jeux normalisés et liste les évolutions du compte."""
    if not old:
        return {"first_import": True}

    old_chars = old.get("characters", {}).get("characters", {})
    new_chars = new.get("characters", {}).get("characters", {})
    new_char_keys = set(new_chars) - set(old_chars)

    const_gains, level_ups, talent_ups = [], [], []
    for k, nc in new_chars.items():
        oc = old_chars.get(k)
        if not oc:
            continue
        if (nc.get("constellation") or 0) > (oc.get("constellation") or 0):
            const_gains.append({"key": k, "from": oc.get("constellation"), "to": nc.get("constellation")})
        if (nc.get("level") or 0) > (oc.get("level") or 0):
            level_ups.append({"key": k, "from": oc.get("level"), "to": nc.get("level")})
        if (nc.get("talents") or {}) != (oc.get("talents") or {}):
            talent_ups.append({"key": k, "from": oc.get("talents"), "to": nc.get("talents")})

    def wkeys(blob: dict[str, Any]) -> dict[str, int]:
        out: dict[str, int] = {}
        for w in blob.get("weapons", {}).get("weapons", {}).values():
            out[w["key"]] = out.get(w["key"], 0) + 1
        return out

    old_w, new_w = wkeys(old), wkeys(new)
    new_weapons = {k: new_w[k] - old_w.get(k, 0) for k in new_w if new_w[k] > old_w.get(k, 0)}

    old_arts = old.get("artifacts", {}).get("artifacts", {})
    new_arts = new.get("artifacts", {}).get("artifacts", {})

    old_mats = old.get("materials", {}).get("materials", {})
    new_mats = new.get("materials", {}).get("materials", {})
    mat_changes = {
        k: {"from": old_mats.get(k, 0), "to": new_mats.get(k, 0)}
        for k in set(old_mats) | set(new_mats)
        if old_mats.get(k, 0) != new_mats.get(k, 0)
    }

    return {
        "first_import": False,
        "new_characters": sorted(new_char_keys),
        "constellation_gains": const_gains,
        "level_ups": level_ups,
        "talent_ups": talent_ups,
        "new_weapons": new_weapons,
        "artifact_count": {"from": len(old_arts), "to": len(new_arts), "delta": len(new_arts) - len(old_arts)},
        "material_changes_count": len(mat_changes),
        "material_changes": dict(sorted(mat_changes.items())[:50]),
    }


# --------------------------------------------------------------------------- #
# Rendu rapport markdown
# --------------------------------------------------------------------------- #
def render_validation_md(result: dict[str, Any], *, source_name: str, snapshot_date: str) -> str:
    v = result["validation"]
    c = v["counts_by_severity"]
    lines = [
        f"# Rapport de validation d'import GOOD — {snapshot_date}",
        "",
        f"- Fichier source : `{source_name}`",
        f"- SHA-256 : `{result['sha256']}`",
        f"- Snapshot : `{result['snapshot']}`",
        f"- Copie brute (lecture seule) : `{result['raw_copy']}`",
        "",
        "## Comptes",
        "",
        f"- Personnages : {v['totals']['characters']}",
        f"- Armes : {v['totals']['weapons']}",
        f"- Artéfacts : {v['totals']['artifacts']}",
        f"- Catégories de matériaux : {v['totals']['materials']}",
        "",
        "## Anomalies par sévérité",
        "",
        f"- BLOCKING : {c['BLOCKING']}",
        f"- ERROR : {c['ERROR']}",
        f"- WARNING : {c['WARNING']}",
        f"- INFO : {c['INFO']}",
        "",
        "## Détail",
        "",
        "| Sévérité | Code | Emplacement | Message |",
        "|---|---|---|---|",
    ]
    order = {s: i for i, s in enumerate(reversed(SEVERITIES))}
    for issue in sorted(v["issues"], key=lambda x: order.get(x["severity"], 99)):
        msg = issue["message"].replace("|", "\\|")
        lines.append(f"| {issue['severity']} | {issue['code']} | `{issue['location']}` | {msg} |")
    if not v["issues"]:
        lines.append("| INFO | — | — | Aucune anomalie. |")
    lines += [
        "",
        "## Personnages non résolus",
        "",
        (", ".join(v["unresolved_characters"]) or "Aucun") + ".",
        "",
        "> Les `unresolvedCharacters` (ex. Traveler) ne doivent pas être utilisés "
        "dans une recommandation principale tant que leurs données de personnage "
        "ne sont pas résolues (nouveau scan ou saisie manuelle).",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Aperçu factuel du compte (données scannées uniquement, aucune supposition)
# --------------------------------------------------------------------------- #
_CRIT_CIRCLET = {"critRate_", "critDMG_"}
_MATERIAL_HIGHLIGHTS = ("Mora", "CrownOfInsight", "HerosWit", "MysticEnhancementOre")


def load_current() -> dict[str, Any]:
    """Charge data/account/current/*.json (lève si aucun import)."""
    cur = account_subdir("current")
    out: dict[str, Any] = {}
    for f in cur.glob("*.json"):
        out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    if "account-profile" not in out:
        raise FileNotFoundError("Aucun import : lance d'abord `irminsul account import-good <fichier>`.")
    return out


def build_overview(current: dict[str, Any]) -> dict[str, Any]:
    """Calcule un aperçu objectif (DONNÉES SCANNÉES). Aucune reco méta ici."""
    chars = current["characters"]["characters"]
    weapons = current["weapons"]["weapons"]
    artifacts = current["artifacts"]["artifacts"]
    materials = current["materials"]["materials"]

    rows = []
    for key, c in chars.items():
        wid = c.get("weapon")
        w = weapons.get(wid) if wid else None
        talents = c.get("talents") or {}
        talent_sum = sum(v for v in talents.values() if isinstance(v, int))
        art_ids = list((c.get("artifacts") or {}).values())
        arts = [artifacts[a] for a in art_ids if a in artifacts]
        circlet = next((a for a in arts if a.get("slotKey") == "circlet"), None)
        has_crit_circlet = bool(circlet and circlet.get("mainStatKey") in _CRIT_CIRCLET)
        set_counts: dict[str, int] = {}
        for a in arts:
            set_counts[a["setKey"]] = set_counts.get(a["setKey"], 0) + 1
        dominant_set = max(set_counts.items(), key=lambda x: x[1])[0] if set_counts else None
        flags = []
        lvl = c.get("level") or 0
        if w and lvl >= 80 and (w.get("level") or 0) <= lvl - 20:
            flags.append(f"arme sous-montée ({w['key']} lvl{w.get('level')})")
        if lvl >= 70 and len(arts) < 5:
            flags.append(f"artéfacts incomplets ({len(arts)}/5)")
        if lvl >= 80 and len(arts) >= 5 and not has_crit_circlet:
            flags.append("pas de couronne crit (vérifier si scaling DEF/HP/soin)")
        score = (
            (100 if lvl >= 90 else lvl)
            + talent_sum * 3
            + len(arts) * 4
            + (8 if has_crit_circlet else 0)
            + (max(set_counts.values()) if set_counts else 0) * 2
        )
        rows.append(
            {
                "key": key,
                "level": lvl,
                "constellation": c.get("constellation"),
                "talents": talents,
                "talent_sum": talent_sum,
                "weapon": (w["key"] if w else None),
                "weapon_level": (w.get("level") if w else None),
                "weapon_refine": (w.get("refinement") if w else None),
                "artifact_count": len(arts),
                "dominant_set": dominant_set,
                "has_crit_circlet": has_crit_circlet,
                "flags": flags,
                "score": score,
            }
        )

    rows.sort(key=lambda r: -r["score"])
    flagged = [r for r in rows if r["flags"]]
    lvl90 = [r for r in rows if r["level"] >= 90]
    free_5star_weapons = [
        w for w in current["weapons"]["weapons"].values()
        if not w["location"] and (w.get("level") or 0) >= 90
    ]
    mats = {k: materials.get(k) for k in _MATERIAL_HIGHLIGHTS if k in materials}

    return {
        "totals": current["account-profile"]["counts"],
        "best_invested": rows[:15],
        "level90_count": len(lvl90),
        "level90_keys": sorted(r["key"] for r in lvl90),
        "equipment_flags": flagged,
        "free_maxed_weapons_sample": sorted({w["key"] for w in free_5star_weapons})[:40],
        "material_highlights": mats,
        "unresolved": list(current["unresolved-data"]["unresolvedCharacters"].keys()),
    }
