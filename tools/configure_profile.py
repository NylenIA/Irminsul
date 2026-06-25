from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "player.yaml"


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def main() -> None:
    payload = yaml.safe_load(PROFILE.read_text(encoding="utf-8")) or {}
    player = payload.setdefault("player", {})
    preferences = player.setdefault("preferences", {})

    print("\nConfiguration du profil Irminsul AI")
    print("Laisse vide une information que tu ne veux pas renseigner.\n")

    player["name"] = ask("Nom ou pseudo", str(player.get("name") or "Nylen"))
    uid = ask("UID Genshin")
    if uid:
        if not uid.isdigit() or not 8 <= len(uid) <= 10:
            raise SystemExit("UID invalide : 8 à 10 chiffres attendus.")
        player["uid"] = uid
    server = ask("Serveur (Europe, America, Asia, TW-HK-MO)", str(player.get("server") or ""))
    if server:
        player["server"] = server
    ping = ask("Ping moyen en ms", str(player.get("average_ping_ms") or ""))
    if ping:
        player["average_ping_ms"] = int(ping)
    leaks = ask("Autoriser les leaks pour la planification future ? (o/n)", "n").lower()
    preferences["allow_leaks_for_planning"] = leaks in {"o", "oui", "y", "yes"}

    PROFILE.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"Profil enregistré dans {PROFILE}")


if __name__ == "__main__":
    main()
