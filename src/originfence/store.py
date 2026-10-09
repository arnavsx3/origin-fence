"""Local SQLite persistence for sessions, events, and policy verdicts."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from originfence.models import Decision


class EventStore:
    """Small local store used by the demo CLI and dashboard."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    pid INTEGER,
                    parent_pid INTEGER,
                    target TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    verdict TEXT,
                    reason TEXT
                )
                """
            )

    def record(self, decision: Decision) -> int:
        """Persist one evaluated event and return its timeline identifier."""
        event = decision.event
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO events (
                    session_id, kind, pid, parent_pid, target, timestamp, metadata, verdict, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.session_id,
                    event.kind.value,
                    event.pid,
                    event.parent_pid,
                    event.target,
                    event.timestamp.isoformat(),
                    json.dumps(event.metadata),
                    decision.verdict.value,
                    decision.reason,
                ),
            )
            return int(cursor.lastrowid)

    def timeline(self, session_id: str | None = None) -> list[dict[str, object]]:
        """Return events in display order, optionally constrained to one session."""
        statement = "SELECT * FROM events"
        parameters: tuple[str, ...] = ()
        if session_id:
            statement += " WHERE session_id = ?"
            parameters = (session_id,)
        statement += " ORDER BY id ASC"

        with self._connect() as connection:
            rows = connection.execute(statement, parameters).fetchall()

        return [
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "kind": row["kind"],
                "pid": row["pid"],
                "parent_pid": row["parent_pid"],
                "target": row["target"],
                "timestamp": row["timestamp"],
                "metadata": json.loads(row["metadata"]),
                "verdict": row["verdict"],
                "reason": row["reason"],
            }
            for row in rows
        ]

    def clear(self) -> None:
        """Remove local demo history."""
        with self._connect() as connection:
            connection.execute("DELETE FROM events")
