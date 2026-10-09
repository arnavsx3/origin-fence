from originfence.dashboard import meaningful_events


def test_dashboard_keeps_blocked_event_and_drops_runtime_noise() -> None:
    events = [
        {"kind": "file_open", "verdict": "allow", "target": "/usr/lib/python3.12/os.py"},
        {"kind": "file_open", "verdict": "allow", "target": "/repo/demo/safe_agent.py"},
        {"kind": "file_open", "verdict": "block", "target": "/repo/demo/fixtures/mock_credentials.txt"},
    ]

    visible = meaningful_events(events)

    assert len(visible) == 2
    assert visible[-1]["verdict"] == "block"
