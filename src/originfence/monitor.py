"""Runtime process and syscall monitoring adapters for the Linux prototype."""

from __future__ import annotations

import re
import subprocess
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from originfence.enforcement import stop_process_group
from originfence.models import Decision, EventKind, RuntimeEvent, Verdict
from originfence.policy import PolicyEngine
from originfence.store import EventStore

_PID_PREFIX = re.compile(r"^(?P<pid>\d+)\s+")
_EXEC = re.compile(r'execve\("(?P<command>[^"]+)"')
_OPEN = re.compile(r'openat\([^,]+, "(?P<path>[^"]+)"')
_IPV4_CONNECT = re.compile(r'sin_addr=inet_addr\("(?P<host>[^"]+)"\)')
_IPV6_CONNECT = re.compile(r'inet_pton\(AF_INET6, "(?P<host>[^"]+)"')


def parse_strace_line(session_id: str, line: str) -> RuntimeEvent | None:
    """Convert one `strace -f` line into an event understood by OriginFence.

    This parser intentionally handles only the three syscalls used in the demo:
    process execution, file opens, and outbound connection attempts.
    """
    pid_match = _PID_PREFIX.search(line)
    pid = int(pid_match.group("pid")) if pid_match else None

    if match := _EXEC.search(line):
        return RuntimeEvent(session_id, EventKind.PROCESS_EXEC, pid=pid, target=match.group("command"))
    if match := _OPEN.search(line):
        return RuntimeEvent(session_id, EventKind.FILE_OPEN, pid=pid, target=match.group("path"))
    if "connect(" in line:
        host_match = _IPV4_CONNECT.search(line) or _IPV6_CONNECT.search(line)
        if host_match:
            return RuntimeEvent(
                session_id,
                EventKind.NETWORK_CONNECT,
                pid=pid,
                target=host_match.group("host"),
            )
    return None


@dataclass(slots=True)
class MonitorResult:
    """The observable result from one guarded command."""

    session_id: str
    return_code: int
    blocked: bool
    event_count: int


def run_guarded_command(
    command: Sequence[str], policy: PolicyEngine, store: EventStore, session_id: str | None = None
) -> MonitorResult:
    """Trace one child command and stop its session on the first blocking verdict.

    `strace` is deliberately used only for a command OriginFence starts itself.
    That means the proof of concept traces no unrelated local process.
    """
    if not command:
        raise ValueError("A command is required.")

    session_id = session_id or uuid.uuid4().hex[:12]
    started = RuntimeEvent(session_id, EventKind.SESSION_STARTED, target=" ".join(command))
    store.record(Decision(Verdict.ALLOW, "Monitored agent session started.", started))

    process = subprocess.Popen(
        ["strace", "-f", "-qq", "-e", "trace=execve,openat,connect", "-s", "512", "--", *command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    blocked = False
    event_count = 0
    assert process.stderr is not None

    for line in process.stderr:
        event = parse_strace_line(session_id, line)
        if event is None:
            continue
        event_count += 1
        decision = policy.evaluate(event)
        store.record(decision)
        if decision.verdict is Verdict.BLOCK and not blocked:
            blocked = True
            stop_process_group(process.pid)
            stopped = RuntimeEvent(
                session_id,
                EventKind.PROCESS_STOPPED,
                pid=process.pid,
                target="process-group",
                metadata={"trigger": event.target},
            )
            store.record(Decision(Verdict.BLOCK, "Stopped the agent-originated process tree.", stopped))

    return_code = process.wait()
    return MonitorResult(session_id, return_code, blocked, event_count)
