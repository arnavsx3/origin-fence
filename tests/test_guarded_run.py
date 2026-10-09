import sys
from pathlib import Path

from originfence.monitor import run_guarded_command
from originfence.policy import PolicyConfig, PolicyEngine
from originfence.store import EventStore


def test_guarded_run_blocks_protected_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / ".env"
    fixture.write_text("DEMO_TOKEN=not-a-real-secret\n")
    script = tmp_path / "reads_fixture.py"
    script.write_text(f"open({str(fixture)!r}).read()\n")
    store = EventStore(tmp_path / "events.sqlite3")
    policy = PolicyEngine(PolicyConfig(protected_paths=[str(fixture)]))

    result = run_guarded_command([sys.executable, str(script)], policy, store, session_id="test")

    assert result.blocked is True
    assert result.captured_event_count > result.security_event_count
    assert any(item["verdict"] == "block" for item in store.timeline("test"))
