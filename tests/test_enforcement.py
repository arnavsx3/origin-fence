import os
import signal

import pytest

from originfence.enforcement import EnforcementError, stop_process_group


def test_stop_process_group_targets_the_negative_group_identifier() -> None:
    calls: list[tuple[int, signal.Signals]] = []

    stop_process_group(1234, lambda pid, sig: calls.append((pid, sig)))

    assert calls == [(-1234, signal.SIGTERM)]


def test_stop_process_group_rejects_its_own_pid() -> None:
    with pytest.raises(EnforcementError):
        stop_process_group(os.getpid())
