from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any

from .paths import db_path
from .source_sync import repository_status


def system_status() -> dict[str, Any]:
    index: dict[str, Any] = {"exists": db_path().exists(), "documents": 0, "indexed_at": None}
    if db_path().exists():
        connection = sqlite3.connect(db_path())
        try:
            row = connection.execute(
                "SELECT COUNT(*), MAX(indexed_at) FROM documents"
            ).fetchone()
            index["documents"] = row[0]
            index["indexed_at"] = row[1]
            if row[1]:
                indexed = datetime.fromisoformat(row[1])
                index["age_hours"] = round(
                    (datetime.now(UTC) - indexed).total_seconds() / 3600, 2
                )
        finally:
            connection.close()
    return {"index": index, "repositories": repository_status()}
