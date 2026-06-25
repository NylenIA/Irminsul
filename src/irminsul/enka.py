from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .paths import cache_dir


def _cache_path(uid: str) -> Path:
    return cache_dir() / f"enka-{uid}.json"


def _read_cache(uid: str) -> dict[str, Any] | None:
    path = _cache_path(uid)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("expires_at", 0) > time.time():
            payload["from_cache"] = True
            return payload
    except (OSError, json.JSONDecodeError):
        return None
    return None


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
)
def fetch_showcase(uid: str, force: bool = False) -> dict[str, Any]:
    if not uid.isdigit() or not 8 <= len(uid) <= 10:
        raise ValueError("UID invalide : 8 à 10 chiffres attendus")
    if not force:
        cached = _read_cache(uid)
        if cached:
            return cached

    headers = {
        "User-Agent": os.getenv(
            "IRMINSUL_USER_AGENT", "IrminsulAI/0.1 (+local Claude Code project)"
        )
    }
    timeout = float(os.getenv("IRMINSUL_ENKA_TIMEOUT", "25"))
    response = httpx.get(f"https://enka.network/api/uid/{uid}/", headers=headers, timeout=timeout)
    enka_errors = {
        400: "UID au mauvais format pour Enka.",
        404: "Aucun joueur trouvé pour cet UID (profil inexistant).",
        424: "Showcase indisponible : maintenance du jeu ou vitrine désactivée/vide.",
        429: "Enka rate-limit atteint. Réutilise le cache ou attends le TTL.",
        500: "Erreur serveur Enka. Réessaie plus tard.",
        503: "Enka temporairement indisponible. Réessaie plus tard.",
    }
    if response.status_code in enka_errors:
        raise RuntimeError(f"Enka [{response.status_code}] : {enka_errors[response.status_code]}")
    response.raise_for_status()
    data = response.json()
    ttl = max(int(data.get("ttl", 300)), 60)
    payload = {
        "uid": uid,
        "fetched_at": time.time(),
        "expires_at": time.time() + ttl,
        "ttl": ttl,
        "from_cache": False,
        "data": data,
    }
    _cache_path(uid).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
