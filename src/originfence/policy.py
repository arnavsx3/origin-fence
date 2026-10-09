"""Deterministic policy evaluation for observed runtime events."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from originfence.models import Decision, EventKind, RuntimeEvent, Verdict


@dataclass(slots=True)
class PolicyConfig:
    """The intentionally small policy surface exposed by the prototype."""

    protected_paths: list[str] = field(default_factory=list)
    allowed_hosts: list[str] = field(default_factory=list)
    block_unknown_after_sensitive_access: bool = True


class PolicyEngine:
    """Apply plain, explainable policy rules to a session's observed actions."""

    def __init__(self, config: PolicyConfig) -> None:
        self.config = config
        self._sessions_with_sensitive_access: set[str] = set()

    def evaluate(self, event: RuntimeEvent) -> Decision:
        """Return one deterministic verdict for an observed event."""
        if event.kind is EventKind.FILE_OPEN and event.target:
            return self._evaluate_file_access(event)

        if event.kind is EventKind.NETWORK_CONNECT and event.target:
            return self._evaluate_network_access(event)

        return Decision(Verdict.ALLOW, "Activity does not match a blocking rule.", event)

    def _evaluate_file_access(self, event: RuntimeEvent) -> Decision:
        if self._is_protected_path(event.target or ""):
            self._sessions_with_sensitive_access.add(event.session_id)
            return Decision(
                Verdict.BLOCK,
                f"Agent-originated process attempted to access protected file: {event.target}",
                event,
            )

        return Decision(Verdict.ALLOW, "File access is outside protected paths.", event)

    def _evaluate_network_access(self, event: RuntimeEvent) -> Decision:
        target = event.target or ""
        if self._host_is_allowed(target):
            return Decision(Verdict.ALLOW, f"Destination is allowlisted: {target}", event)

        if (
            self.config.block_unknown_after_sensitive_access
            and event.session_id in self._sessions_with_sensitive_access
        ):
            return Decision(
                Verdict.BLOCK,
                f"Blocked unapproved destination after sensitive-file access: {target}",
                event,
            )

        return Decision(Verdict.ASK, f"Destination requires developer approval: {target}", event)

    def _is_protected_path(self, target: str) -> bool:
        absolute_target = str(Path(target).expanduser())
        return any(
            fnmatch(absolute_target, str(Path(pattern).expanduser()))
            or fnmatch(target, pattern)
            for pattern in self.config.protected_paths
        )

    def _host_is_allowed(self, target: str) -> bool:
        host = target.split(":", maxsplit=1)[0]
        return any(host == allowed or host.endswith(f".{allowed}") for allowed in self.config.allowed_hosts)
