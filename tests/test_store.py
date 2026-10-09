from pathlib import Path

from originfence.models import Decision, EventKind, RuntimeEvent, Verdict
from originfence.store import EventStore


def test_store_returns_a_serialisable_timeline(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.sqlite3")
    event = RuntimeEvent("demo", EventKind.FILE_OPEN, pid=42, target="/tmp/.env")
    store.record(Decision(Verdict.BLOCK, "Protected path", event))

    timeline = store.timeline("demo")

    assert timeline[0]["kind"] == "file_open"
    assert timeline[0]["verdict"] == "block"
    assert timeline[0]["metadata"] == {}
