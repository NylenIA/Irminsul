"""Tests du mode d'audit projet (irminsul.audit)."""

from __future__ import annotations

import json
from pathlib import Path

from irminsul.audit import render_audit_md, run_audit


def test_audit_runs_on_real_project() -> None:
    result = run_audit()
    assert "summary" in result and "findings" in result
    for sev in ("CRITIQUE", "IMPORTANT", "OK"):
        assert sev in result["summary"]
    # Le rapport markdown se génère sans erreur.
    md = render_audit_md(result)
    assert md.startswith("# Rapport d'audit")


def _make_min_project(root: Path) -> None:
    (root / "src" / "irminsul").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "skills").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "config").mkdir()
    (root / "CLAUDE.md").write_text("RESEARCH_POLICY", encoding="utf-8")
    (root / "pyproject.toml").write_text("", encoding="utf-8")
    (root / "config" / "sources.yaml").write_text("sources: []", encoding="utf-8")
    (root / "docs" / "RESEARCH_POLICY.md").write_text("policy", encoding="utf-8")
    (root / ".mcp.json").write_text(json.dumps({"mcpServers": {"irminsul": {}}}), encoding="utf-8")


def test_audit_flags_missing_gitignore_privacy(tmp_path: Path) -> None:
    """Sécurité/confidentialité : absence de gitignore du compte = CRITIQUE."""
    _make_min_project(tmp_path)
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")  # n'ignore pas data/account
    result = run_audit(root=tmp_path)
    privacy = [f for f in result["findings"] if f["area"] == "confidentialité"]
    assert privacy and privacy[0]["severity"] == "CRITIQUE"


def test_audit_ok_when_privacy_protected(tmp_path: Path) -> None:
    _make_min_project(tmp_path)
    (tmp_path / ".gitignore").write_text(
        "data/account/\nprofiles/player.yaml\n", encoding="utf-8"
    )
    result = run_audit(root=tmp_path)
    privacy = [f for f in result["findings"] if f["area"] == "confidentialité"]
    assert privacy and privacy[0]["severity"] == "OK"


def test_audit_flags_missing_research_policy(tmp_path: Path) -> None:
    _make_min_project(tmp_path)
    (tmp_path / "docs" / "RESEARCH_POLICY.md").unlink()
    (tmp_path / ".gitignore").write_text("data/account/\nprofiles/player.yaml\n", encoding="utf-8")
    result = run_audit(root=tmp_path)
    arch = [f for f in result["findings"]
            if f["area"] == "architecture" and "RESEARCH_POLICY" in f["message"]]
    assert arch and arch[0]["severity"] == "CRITIQUE"
