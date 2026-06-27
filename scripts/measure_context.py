#!/usr/bin/env python
"""Mesure reproductible du coût en contexte/tokens du projet (Phase 0).

Déterministe, sans appel API. Estime des tokens (~chars/4) à titre indicatif et
sépare le contexte PERMANENT (toujours chargé) du contexte À LA DEMANDE.

Usage : python scripts/measure_context.py [--json out.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _stat(rel: str) -> dict[str, int]:
    p = ROOT / rel
    if not p.exists():
        return {"exists": 0, "lines": 0, "chars": 0, "tokens_est": 0}
    text = p.read_text(encoding="utf-8", errors="replace")
    chars = len(text)
    return {"exists": 1, "lines": text.count("\n") + 1, "chars": chars,
            "tokens_est": round(chars / 4)}


def _group(pattern: str) -> dict[str, object]:
    files = sorted(glob.glob(str(ROOT / pattern), recursive=True))
    total = {"files": len(files), "lines": 0, "chars": 0, "tokens_est": 0}
    for f in files:
        t = Path(f).read_text(encoding="utf-8", errors="replace")
        total["lines"] += t.count("\n") + 1
        total["chars"] += len(t)
    total["tokens_est"] = round(total["chars"] / 4)
    return total


def measure() -> dict[str, object]:
    # Contexte PERMANENT : chargé à chaque session/agent principal.
    permanent = {
        "CLAUDE.md": _stat("CLAUDE.md"),
        "agent_memory_MEMORY.md": _stat(".claude/agent-memory/irminsul-orchestrator/MEMORY.md"),
        "orchestrator_agent": _stat(".claude/agents/irminsul-orchestrator.md"),
    }
    perm_tokens = sum(v["tokens_est"] for v in permanent.values())

    on_demand = {
        "subagents": _group(".claude/agents/*.md"),
        "skills": _group(".claude/skills/*/SKILL.md"),
        "path_rules": _group(".claude/rules/*.md"),
        "agent_memory_files": _group(".claude/agent-memory/**/*.md"),
        "project_docs": _group("docs/**/*.md"),
    }

    mcp = _stat(".mcp.json")
    # Outils MCP irminsul connus (schémas envoyés au modèle quand le serveur est chargé).
    mcp_tools = [
        "irminsul_status", "refresh_knowledge", "search_knowledge",
        "calculate_direct_hit", "calculate_amplifying_multiplier",
        "calculate_transformative_reaction", "run_gcsim", "score_leak",
        "import_enka_showcase", "inspect_good_export",
    ]

    heavy = {
        "data_account": _group("data/account/**/*.json"),
        "good_raw": _group("data/account/raw/*.json"),
        "sqlite_db_bytes": (os.path.getsize(ROOT / "data/irminsul.db")
                            if (ROOT / "data/irminsul.db").exists() else 0),
        "sources_files": len(glob.glob(str(ROOT / "data/sources/**/*"), recursive=True)),
    }

    return {
        "permanent_context": permanent,
        "permanent_tokens_est": perm_tokens,
        "on_demand_context": on_demand,
        "mcp": {"config": mcp, "tool_count": len(mcp_tools), "tools": mcp_tools},
        "heavy_excluded_from_context": heavy,
        "counts": {
            "subagents": on_demand["subagents"]["files"],
            "skills": on_demand["skills"]["files"],
            "path_rules": on_demand["path_rules"]["files"],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    data = measure()
    out = json.dumps(data, ensure_ascii=False, indent=2)
    if args.json:
        Path(args.json).write_text(out, encoding="utf-8")
    # Résumé compact sur stdout.
    p = data["permanent_context"]
    print(f"PERMANENT tokens_est: {data['permanent_tokens_est']}")
    print(f"  CLAUDE.md: {p['CLAUDE.md']['lines']} lignes / {p['CLAUDE.md']['tokens_est']} tok")
    print(f"  MEMORY.md: {p['agent_memory_MEMORY.md']['lines']} lignes / {p['agent_memory_MEMORY.md']['tokens_est']} tok")
    print(f"  orchestrator: {p['orchestrator_agent']['lines']} lignes / {p['orchestrator_agent']['tokens_est']} tok")
    print(f"ON-DEMAND skills: {data['counts']['skills']} | subagents: {data['counts']['subagents']} | path_rules: {data['counts']['path_rules']}")
    print(f"MCP tools: {data['mcp']['tool_count']}")


if __name__ == "__main__":
    main()
