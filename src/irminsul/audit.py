"""Mode d'audit projet d'Irminsul AI (cf. docs/RESEARCH_POLICY.md §11).

Vérifie architecture, agents, skills, MCP, dépendances, sources, fraîcheur, import
GOOD, gcsim, DPS, leaks, tests, docs, sécurité/confidentialité, compat Windows et
cohérence des prompts. Produit un rapport classé par sévérité.
"""

from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from typing import Any

from .paths import project_root

SEVERITIES = ("CRITIQUE", "IMPORTANT", "INCOHERENCE", "RISQUE", "OBSOLETE",
              "RECOMMANDATION", "OK")


def _finding(sev: str, area: str, message: str, fix: str = "") -> dict[str, str]:
    return {"severity": sev, "area": area, "message": message, "fix": fix}


def run_audit(root: Path | None = None) -> dict[str, Any]:
    """Audite le projet et renvoie {findings, summary}."""
    root = root or project_root()
    f: list[dict[str, str]] = []

    def exists(rel: str) -> bool:
        return (root / rel).exists()

    # --- Architecture ---
    required = [
        "CLAUDE.md", "pyproject.toml", "src/irminsul", "tests",
        "config/sources.yaml", ".claude/agents", ".claude/skills",
        "docs/RESEARCH_POLICY.md", ".mcp.json",
    ]
    for rel in required:
        if exists(rel):
            f.append(_finding("OK", "architecture", f"présent : {rel}"))
        else:
            sev = "CRITIQUE" if rel in ("CLAUDE.md", "src/irminsul", "docs/RESEARCH_POLICY.md") else "IMPORTANT"
            f.append(_finding(sev, "architecture", f"manquant : {rel}", f"créer {rel}"))

    # --- Agents ---
    agents_dir = root / ".claude" / "agents"
    if agents_dir.exists():
        agents = list(agents_dir.glob("*.md"))
        f.append(_finding("OK", "agents", f"{len(agents)} agents détectés"))
        for a in agents:
            txt = a.read_text(encoding="utf-8", errors="replace")
            if "name:" not in txt:
                f.append(_finding("IMPORTANT", "agents", f"{a.name} sans frontmatter 'name'",
                                  "ajouter le frontmatter"))
            if "RESEARCH_POLICY" not in txt and "research_policy" not in txt:
                f.append(_finding("RECOMMANDATION", "prompts",
                                  f"{a.name} ne référence pas la politique de recherche",
                                  "ajouter un pointeur vers docs/RESEARCH_POLICY.md"))

    # --- Skills ---
    skills_dir = root / ".claude" / "skills"
    if skills_dir.exists():
        skills = list(skills_dir.glob("*/SKILL.md"))
        f.append(_finding("OK", "skills", f"{len(skills)} skills détectés"))
        for s in skills:
            txt = s.read_text(encoding="utf-8", errors="replace")
            if "name:" not in txt or "description:" not in txt:
                f.append(_finding("INCOHERENCE", "skills",
                                  f"{s.parent.name} : frontmatter incomplet",
                                  "ajouter name + description"))

    # --- MCP ---
    if exists(".mcp.json"):
        try:
            mcp = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            if "irminsul" in (mcp.get("mcpServers") or {}):
                f.append(_finding("OK", "mcp", "serveur MCP 'irminsul' configuré"))
            else:
                f.append(_finding("IMPORTANT", "mcp", "serveur 'irminsul' absent de .mcp.json"))
        except json.JSONDecodeError:
            f.append(_finding("CRITIQUE", "mcp", ".mcp.json illisible (JSON invalide)", "corriger le JSON"))

    # --- Dépendances / modules clés ---
    for mod in ("irminsul.damage", "irminsul.reaction", "irminsul.leaks",
                "irminsul.research_policy", "irminsul.account", "irminsul.team_optimizer"):
        try:
            import_module(mod)
            f.append(_finding("OK", "dépendances", f"import OK : {mod}"))
        except Exception as exc:  # noqa: BLE001 — on veut classer toute erreur d'import
            f.append(_finding("CRITIQUE", "dépendances", f"import KO : {mod} ({exc})",
                              "corriger l'import / réinstaller"))

    # --- Sources & fraîcheur ---
    try:
        from .status import system_status
        st = system_status()
        idx = st.get("index", {})
        if not idx.get("exists"):
            f.append(_finding("IMPORTANT", "sources", "index local absent",
                              "lancer `irminsul update`"))
        else:
            age = idx.get("age_hours")
            if age is None:
                f.append(_finding("RISQUE", "fraîcheur", "index sans date"))
            elif age > 24:
                f.append(_finding("OBSOLETE", "fraîcheur", f"index âgé de {age} h (>24 h)",
                                  "lancer `irminsul update`"))
            else:
                f.append(_finding("OK", "fraîcheur", f"index frais ({age} h)"))
        repos = st.get("repositories", [])
        missing = [r["name"] for r in repos if r.get("enabled") and not r.get("exists")]
        if missing:
            f.append(_finding("IMPORTANT", "sources", f"sources actives absentes : {missing}",
                              "lancer `irminsul update`"))
    except Exception as exc:  # noqa: BLE001
        f.append(_finding("RISQUE", "sources", f"status indisponible ({exc})"))

    # --- gcsim ---
    if exists("tools/bin/gcsim.exe") or exists("tools/bin/gcsim"):
        f.append(_finding("OK", "gcsim", "binaire gcsim présent"))
    else:
        f.append(_finding("RISQUE", "gcsim", "binaire gcsim absent",
                          "lancer tools/install_gcsim.py"))

    # --- Import GOOD (compte) ---
    if exists("data/account/current/account-profile.json"):
        f.append(_finding("OK", "import-good", "profil de compte normalisé présent"))
    else:
        f.append(_finding("RECOMMANDATION", "import-good", "aucun compte importé",
                          "lancer `account import-good <fichier>`"))

    # --- Tests ---
    tests = list((root / "tests").glob("test_*.py")) if exists("tests") else []
    if len(tests) >= 5:
        f.append(_finding("OK", "tests", f"{len(tests)} fichiers de test"))
    else:
        f.append(_finding("IMPORTANT", "tests", f"peu de tests ({len(tests)})", "ajouter des tests"))

    # --- Sécurité / confidentialité ---
    gi = (root / ".gitignore").read_text(encoding="utf-8") if exists(".gitignore") else ""
    if "data/account/" in gi and "profiles/player.yaml" in gi:
        f.append(_finding("OK", "confidentialité", "compte joueur et profil ignorés par git"))
    else:
        f.append(_finding("CRITIQUE", "confidentialité",
                          "data/account/ ou profiles/player.yaml NON ignoré",
                          "ajouter au .gitignore (données personnelles)"))

    # --- Compat Windows ---
    if exists("scripts/validate.ps1") and exists("scripts/bootstrap.ps1"):
        f.append(_finding("OK", "windows", "scripts PowerShell présents"))
    else:
        f.append(_finding("RECOMMANDATION", "windows", "scripts PowerShell incomplets"))

    # --- Cohérence des prompts (politique centrale) ---
    claude = (root / "CLAUDE.md").read_text(encoding="utf-8") if exists("CLAUDE.md") else ""
    if "RESEARCH_POLICY" in claude:
        f.append(_finding("OK", "prompts", "CLAUDE.md référence la politique de recherche"))
    else:
        f.append(_finding("RECOMMANDATION", "prompts",
                          "CLAUDE.md ne référence pas docs/RESEARCH_POLICY.md",
                          "ajouter un renvoi"))

    summary = {sev: sum(1 for x in f if x["severity"] == sev) for sev in SEVERITIES}
    summary["blocking"] = summary["CRITIQUE"]
    return {"root": str(root), "findings": f, "summary": summary}


def render_audit_md(result: dict[str, Any]) -> str:
    s = result["summary"]
    lines = [
        "# Rapport d'audit Irminsul AI",
        "",
        f"Racine : `{result['root']}`",
        "",
        "## Synthèse",
        "",
        f"- CRITIQUE : {s['CRITIQUE']} · IMPORTANT : {s['IMPORTANT']} · "
        f"INCOHÉRENCE : {s['INCOHERENCE']} · RISQUE : {s['RISQUE']} · "
        f"OBSOLÈTE : {s['OBSOLETE']} · RECOMMANDATION : {s['RECOMMANDATION']} · OK : {s['OK']}",
        "",
        "## Constats (hors OK)",
        "",
        "| Sévérité | Domaine | Constat | Correctif |",
        "|---|---|---|---|",
    ]
    order = {sev: i for i, sev in enumerate(SEVERITIES)}
    for it in sorted(result["findings"], key=lambda x: order[x["severity"]]):
        if it["severity"] == "OK":
            continue
        msg = it["message"].replace("|", "\\|")
        fix = (it["fix"] or "—").replace("|", "\\|")
        lines.append(f"| {it['severity']} | {it['area']} | {msg} | {fix} |")
    lines += ["", f"_Éléments vérifiés sans problème (OK) : {s['OK']}._"]
    return "\n".join(lines) + "\n"
