"""Safe process-tree enforcement actions for blocking verdicts."""

from __future__ import annotations

import os
import signal
from collections.abc import Callable


class EnforcementError(RuntimeError):
    """Raised when a process tree cannot be stopped safely."""


def stop_process_group(pid: int, kill: Callable[[int, signal.Signals], None] = os.kill) -> None:
    """Stop the isolated process group launched for one monitored session.

    The launcher creates a new session for the child command, so its PID is also
    its process-group identifier. This keeps enforcement scoped to the demo
    process tree rather than scanning or affecting unrelated system processes.
    """
    if pid <= 0:
        raise EnforcementError("A positive process identifier is required.")
    if pid == os.getpid():
        raise EnforcementError("OriginFence will not stop its own process.")

    try:
        kill(-pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError as error:
        raise EnforcementError(f"Permission denied while stopping process group {pid}.") from error
