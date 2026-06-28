"""Tests du serveur MCP et de la dégradation quand une source est indisponible."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from irminsul import source_sync
from irminsul.mcp_server import mcp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = PROJECT_ROOT / "scripts" / "mcp_launch.py"

EXPECTED_TOOLS = {
    "irminsul_status",
    "refresh_knowledge",
    "search_knowledge",
    "calculate_direct_hit",
    "calculate_transformative_reaction",
    "calculate_amplifying_multiplier",
    "score_leak",
    "import_enka_showcase",
    "inspect_good_export",
    "run_gcsim",
}


def test_mcp_exposes_exactly_ten_tools() -> None:
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert names == EXPECTED_TOOLS
    assert len(tools) == 10


def test_search_returns_empty_when_index_unavailable(monkeypatch, tmp_path) -> None:
    """Si la base locale est absente (source indisponible), la recherche ne
    plante pas : elle renvoie une liste vide au lieu d'inventer un résultat."""
    missing = tmp_path / "no-such.db"
    monkeypatch.setattr(source_sync, "db_path", lambda: Path(missing))
    assert source_sync.search_index("furina vaporize") == []


def test_search_empty_query_returns_empty() -> None:
    assert source_sync.search_index("   ") == []


@pytest.mark.integration
@pytest.mark.skipif(
    sys.platform != "win32",
    reason="régression stdio spécifique à Windows (os.execv) ; cible réelle = Windows",
)
def test_launcher_stdio_handshake() -> None:
    """Le serveur démarre via scripts/mcp_launch.py et répond en JSON-RPC stdio.

    Régression : sous Windows, os.execv cassait l'héritage des pipes stdio et le
    client MCP (Claude Code) perdait la connexion. Le launcher doit répondre à
    `initialize` puis `tools/list` avec 10 outils. Le contrat « 10 outils » est
    aussi couvert (toutes plateformes) par test_mcp_exposes_exactly_ten_tools.
    """
    venv_python = PROJECT_ROOT / ".venv" / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    if not venv_python.exists():
        pytest.skip("environnement virtuel absent")
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    stdin = "".join(json.dumps(m) + "\n" for m in messages)
    proc = subprocess.run(
        [sys.executable, str(LAUNCHER)],
        input=stdin, capture_output=True, text=True, timeout=90,
        cwd=str(PROJECT_ROOT),
    )
    responses = {}
    for line in proc.stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" in obj:
            responses[obj["id"]] = obj
    assert "result" in responses.get(1, {}), proc.stderr[-500:]
    tools = responses.get(2, {}).get("result", {}).get("tools", [])
    assert len(tools) == 10
