from __future__ import annotations

import fnmatch
import json
import os
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .config import sources_config
from .paths import db_path, sources_dir

TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".js", ".ts", ".tsx", ".go", ".py"
}


def _run(command: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout.strip()


def sync_repositories() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for source in sources_config().get("sources", []):
        if not source.get("enabled", False):
            continue
        target = sources_dir() / source["id"]
        try:
            if (target / ".git").exists():
                _run(["git", "fetch", "--depth", "1", "origin", "HEAD"], target)
                _run(["git", "reset", "--hard", "FETCH_HEAD"], target)
                action = "updated"
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                _run(["git", "clone", "--depth", "1", source["url"], str(target)])
                action = "cloned"
            commit = _run(["git", "rev-parse", "HEAD"], target)
            results.append({"id": source["id"], "ok": True, "action": action, "commit": commit})
        except Exception as exc:  # noqa: BLE001
            results.append({"id": source["id"], "ok": False, "error": str(exc)})
    return results


def _pattern_matches(path: Path, pattern: str) -> bool:
    posix = path.as_posix()
    variants = {pattern, pattern.replace("/**/", "/")}
    return any(fnmatch.fnmatch(posix, item) or path.match(item) for item in variants)


def _iter_documents(source: dict[str, Any]) -> Iterable[tuple[Path, str]]:
    """Itère les fichiers d'une source en globant directement chaque motif d'include.

    On évite de parcourir tout l'arbre (certaines sources comme genshin-db ont
    >100k fichiers) : `root.glob(pattern)` ne visite que les chemins pertinents.
    Un plafond par source (IRMINSUL_MAX_FILES_PER_SOURCE) sert de garde-fou.
    """
    root = sources_dir() / source["id"]
    if not root.exists():
        return
    max_bytes = int(float(os.getenv("IRMINSUL_MAX_FILE_MB", "8")) * 1024 * 1024)
    max_files = int(os.getenv("IRMINSUL_MAX_FILES_PER_SOURCE", "20000"))
    include = source.get("include", ["**/*"])
    exclude = source.get("exclude", [])
    seen: set[Path] = set()
    yielded = 0
    for pattern in include:
        for file_path in root.glob(pattern):
            if file_path in seen or not file_path.is_file():
                continue
            if file_path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            relative = file_path.relative_to(root)
            if any(_pattern_matches(relative, item) for item in exclude):
                continue
            seen.add(file_path)
            try:
                if file_path.stat().st_size > max_bytes:
                    continue
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                if file_path.suffix.lower() == ".json":
                    try:
                        text = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
                    except json.JSONDecodeError:
                        pass
                if not text.strip():
                    continue
                yield relative, text
                yielded += 1
                if yielded >= max_files:
                    return
            except OSError:
                continue


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY,
          source_id TEXT NOT NULL,
          source_name TEXT NOT NULL,
          kind TEXT NOT NULL,
          tier TEXT NOT NULL,
          path TEXT NOT NULL,
          content TEXT NOT NULL,
          indexed_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
          content, source_id UNINDEXED, path UNINDEXED, content='documents', content_rowid='id'
        )
        """
    )
    return connection


def rebuild_index() -> dict[str, Any]:
    config = sources_config()
    connection = _connect()
    inserted = 0
    by_source: dict[str, int] = {}
    now = datetime.now(UTC).isoformat()
    with connection:
        connection.execute("DELETE FROM documents_fts")
        connection.execute("DELETE FROM documents")
        for source in config.get("sources", []):
            if not source.get("enabled", False):
                continue
            count = 0
            for relative, content in _iter_documents(source):
                cursor = connection.execute(
                    """
                    INSERT INTO documents(source_id, source_name, kind, tier, path, content, indexed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source["id"], source["name"], source["kind"], source["tier"],
                        relative.as_posix(), content, now,
                    ),
                )
                connection.execute(
                    "INSERT INTO documents_fts(rowid, content, source_id, path) VALUES (?, ?, ?, ?)",
                    (cursor.lastrowid, content, source["id"], relative.as_posix()),
                )
                inserted += 1
                count += 1
            by_source[source["id"]] = count
    connection.close()
    return {"documents": inserted, "by_source": by_source, "indexed_at": now}


def search_index(query: str, limit: int = 8, kinds: list[str] | None = None) -> list[dict[str, Any]]:
    if not db_path().exists():
        return []
    cleaned = " ".join(token for token in query.replace('"', " ").split() if token)
    if not cleaned:
        return []
    fts_query = " OR ".join(f'"{token}"' for token in cleaned.split())
    connection = _connect()
    sql = """
        SELECT d.source_id, d.source_name, d.kind, d.tier, d.path,
               snippet(documents_fts, 0, '[', ']', ' … ', 28) AS snippet,
               bm25(documents_fts) AS rank, d.indexed_at
        FROM documents_fts
        JOIN documents d ON d.id = documents_fts.rowid
        WHERE documents_fts MATCH ?
    """
    params: list[Any] = [fts_query]
    if kinds:
        placeholders = ",".join("?" for _ in kinds)
        sql += f" AND d.kind IN ({placeholders})"
        params.extend(kinds)
    sql += " ORDER BY rank LIMIT ?"
    params.append(max(1, min(limit, 50)))
    rows = connection.execute(sql, params).fetchall()
    connection.close()
    return [
        {
            "source_id": row[0], "source_name": row[1], "kind": row[2], "tier": row[3],
            "path": row[4], "snippet": row[5], "rank": row[6], "indexed_at": row[7],
        }
        for row in rows
    ]


def repository_status() -> list[dict[str, Any]]:
    status: list[dict[str, Any]] = []
    for source in sources_config().get("sources", []):
        target = sources_dir() / source["id"]
        item: dict[str, Any] = {
            "id": source["id"], "name": source["name"], "enabled": source.get("enabled", False),
            "exists": target.exists(), "tier": source["tier"], "kind": source["kind"],
        }
        if (target / ".git").exists():
            try:
                item["commit"] = _run(["git", "rev-parse", "--short", "HEAD"], target)
                item["commit_date"] = _run(["git", "show", "-s", "--format=%cI", "HEAD"], target)
            except Exception as exc:  # noqa: BLE001
                item["error"] = str(exc)
        status.append(item)
    return status
