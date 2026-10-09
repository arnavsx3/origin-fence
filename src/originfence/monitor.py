"""Runtime process and syscall monitoring adapters for the Linux prototype."""

from __future__ import annotations

import re

from originfence.models import EventKind, RuntimeEvent

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
