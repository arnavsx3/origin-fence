"""Shared event and verdict models for the local security timeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class EventKind(StrEnum):
    """The small set of runtime actions the proof of concept understands."""

    SESSION_STARTED = "session_started"
    PROCESS_EXEC = "process_exec"
    FILE_OPEN = "file_open"
    NETWORK_CONNECT = "network_connect"
    PROCESS_STOPPED = "process_stopped"


class Verdict(StrEnum):
    """A deterministic policy outcome."""

    ALLOW = "allow"
    ASK = "ask"
    BLOCK = "block"


def is_security_relevant(kind: str | EventKind, target: str | None, verdict: str | Verdict) -> bool:
    """Keep dashboard and terminal summaries focused on meaningful evidence."""
    return verdict != Verdict.ALLOW and verdict != Verdict.ALLOW.value or (
        kind != EventKind.FILE_OPEN and kind != EventKind.FILE_OPEN.value
    ) or "/demo/" in (target or "")


@dataclass(slots=True)
class RuntimeEvent:
    """One observed action from a monitored agent-originated process tree."""

    session_id: str
    kind: EventKind
    pid: int | None = None
    parent_pid: int | None = None
    target: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-friendly event data for persistence and the dashboard."""
        payload = asdict(self)
        payload["kind"] = self.kind.value
        payload["timestamp"] = self.timestamp.isoformat()
        return payload


@dataclass(slots=True)
class Decision:
    """A policy decision with the reason shown to the developer."""

    verdict: Verdict
    reason: str
    event: RuntimeEvent

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-friendly decision data."""
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "event": self.event.to_dict(),
        }
