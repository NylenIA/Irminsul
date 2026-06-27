"""Tests de non-régression de l'infrastructure d'efficacité tokens (Phase 0)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_measure_context_structure() -> None:
    m = _load("measure_context").measure()
    assert "permanent_context" in m and "on_demand_context" in m
    assert isinstance(m["permanent_tokens_est"], int)
    assert m["permanent_context"]["CLAUDE.md"]["exists"] == 1
    assert m["mcp"]["tool_count"] >= 1


def test_index_repo_finds_python_symbols() -> None:
    data = _load("index_repo").build()
    assert data["file_count"] > 0
    acc = data["files"].get("src/irminsul/account.py")
    assert acc and "symbols" in acc
    names = {s["name"] for s in acc["symbols"]}
    assert "import_good" in names  # symbole connu localisé


def test_peek_json_does_not_dump_full_values() -> None:
    peek = _load("peek_json")
    shaped = peek.shape({"big": "x" * 500, "n": 3, "lst": [1, 2, 3]})
    assert "x" * 500 not in json.dumps(shaped)  # le contenu volumineux n'est PAS recopié
    assert "len=500" in json.dumps(shaped)


def test_run_logged_preserves_real_exit_code(tmp_path: Path) -> None:
    # Une commande qui échoue doit renvoyer un code != 0 (jamais masqué par un pipe).
    res = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_logged.py"), "--label", "t", "--",
         sys.executable, "-c", "import sys; sys.exit(3)"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert res.returncode == 3
    assert "exit=3" in res.stdout
    assert (ROOT / ".irminsul" / "logs").exists()


def test_token_budgets_valid_and_guarantees_on() -> None:
    cfg = json.loads((ROOT / "config" / "token-budgets.json").read_text(encoding="utf-8"))
    for key in ("permanent_context", "tool_output", "file_reads", "hard_guarantees"):
        assert key in cfg
    g = cfg["hard_guarantees"]
    assert g["no_secret_in_git_or_logs"] and g["no_full_good_to_model"]
    assert g["no_result_modification_for_budget"] and g["no_test_reduction_for_budget"]


def test_claude_md_under_gate_limit() -> None:
    lines = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").count("\n") + 1
    assert lines < 200  # porte Phase 0 : CLAUDE.md doit rester compact
